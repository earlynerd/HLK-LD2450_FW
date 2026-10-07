"""Loopback HTTP server, bounded USB acquisition, and replay lifecycle."""
import argparse
from collections import deque
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import queue
import secrets
import sys
import threading
import time
from urllib.parse import urlparse, parse_qs
from datetime import datetime

import serial
from serial.tools import list_ports

from .processing import Pipeline, DEFAULT_SETTINGS, validate_settings

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "firmware" / "tools"))
from frame_stream import (Parser, Frames, save_frame, encode_command,  # Existing integrity boundary.
                          CONTROL_READ, CONTROL_WRITE, CONTROL_REINIT, CONTROL_STATUS)

WEB = Path(__file__).with_name("web")
OUTPUT = ROOT / "output" / "live_radar"
USB_VID, USB_PID, USB_SERIAL = 0x4c4a, 0x4155, "LD2450-STREAM-01"
RECORD_LIMIT = 1024 * 1024 * 1024
REGISTER_TABLE = ROOT / "output" / "evb1122_analysis" / "register_write_table.json"
REGISTER_FINDINGS = Path(__file__).with_name("register_findings.json")  # Hand-edited bench findings.
READ_CHUNK = 4          # Registers per READ: fits the device's between-frame window.
# One command in flight: the SDK's bulk-OUT read copies every waiting packet
# unbounded (see ld2450_usb_read in usb_stream.c), so the device must never
# have more than one short packet pending. Bench: replies take 40-200 ms. Older
# firmware lost command packets (SDK FlushFIFO race, see usb_stream.c), so
# READ/WRITE are resent; a repeated WRITE rewrites the same value. REINIT never is.
REPLY_TIMEOUT_S = 1.5   # A 4-register READ may span several frame gaps.
REINIT_TIMEOUT_S = 3.0
COMMAND_ATTEMPTS = 4


def usb_ports():
    return [p.device for p in list_ports.comports()
            if (p.vid, p.pid, p.serial_number) == (USB_VID, USB_PID, USB_SERIAL)]


def register_notes():
    """Stock mode-2 startup value (last write), working interpretation and bench findings per register."""
    notes = {}
    try:
        rows = json.loads(REGISTER_TABLE.read_text(encoding="utf-8"))["rows"]
    except (OSError, ValueError, KeyError):
        rows = []
    try:
        findings = json.loads(REGISTER_FINDINGS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        findings = {}
    for key, item in findings.items():
        if not key.startswith("_") and isinstance(item, dict):
            notes.setdefault(int(key, 16), dict(function="", writes=[])).update(
                finding=item.get("finding", ""), evidence=item.get("evidence", ""))
    for row in rows:
        reg = int(row["register"], 16)
        entry = notes.setdefault(reg, dict(function=row["function"], writes=[]))
        entry["function"] = row["function"]
        entry["writes"].append(int(row["mode2_value"], 16))
        entry["stock"] = int(row["mode2_value"], 16)
        entry["meaning"] = row["mode2_meaning"]
    return notes


def new_folder(kind):
    folder = OUTPUT / (datetime.now().strftime("%Y%m%d-%H%M%S-") + kind + "-" + secrets.token_hex(3))
    folder.mkdir(parents=True, exist_ok=False)
    return folder


class Viewer:
    def __init__(self):
        self.lock = threading.RLock()
        self.lifecycle = threading.Lock()
        self.pipeline_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.threads = []
        self.transport = None
        self.pipeline = Pipeline()
        self.settings = dict(DEFAULT_SETTINGS)
        self.latest = self.raw_frame = None
        self.version = self.generation = 0
        self.last_frame_at = None
        self.last_abort_at = None
        self.status, self.source, self.error = "disconnected", "", ""
        self.stats = {}
        self.record = None
        self.record_result = None
        self.started = time.monotonic()
        self.sources = self.discover_sources()
        self.write_lock = threading.Lock()
        self.notes = register_notes()
        self.reset_registers()
        self.reset_stats()

    def reset_registers(self):
        self.registers = {}           # reg -> dict(value, op, generation, at)
        self.register_log = deque(maxlen=200)
        self.pending = {}             # tag -> dict(op, register, count, value, sent)
        self.register_generation = None
        self.next_tag = 1
        self.commands = queue.Queue()  # Sent one at a time by _send_commands.

    @staticmethod
    def discover_sources():
        paths = sorted((ROOT / "output" / "stream_bench").glob("*/stream.ldf"))
        paths += sorted(OUTPUT.glob("*/stream.ldf")) if OUTPUT.exists() else []
        return {str(i): p for i, p in enumerate(paths)}

    def reset_stats(self):
        self.stats = dict(received_bytes=0, complete_frames=0, rejected_frames=0,
                          parser_errors=0, discarded_bytes=0, protocol_errors=0,
                          device_skipped=0, device_rejected=0, device_queue_peak=0,
                          processing_drops=0, timing_outliers=0, replay_loops=0,
                          wire_kbps=0, frames_per_second=0, truncated_tail=False,
                          device_aborts=0, queue_aborts=0, cpu_aborts=0, other_aborts=0,
                          invalid_frames=0, last_abort=None)
        self.last_abort_at = None
        self.rate_at = time.monotonic()
        self.rate_bytes = self.rate_frames = 0

    def state(self, since=-1):
        with self.lock:
            now = time.monotonic()
            age = None if self.last_frame_at is None else round(now - self.last_frame_at, 2)
            stats = dict(self.stats)
            if age is None or age > 2:
                stats["frames_per_second"] = 0
            if now - self.rate_at > 2:
                stats["wire_kbps"] = 0
            result = dict(status=self.status, source=self.source, error=self.error,
                          stats=stats, version=self.version, generation=self.generation,
                          last_frame_age_s=age, settings=self.settings,
                          last_abort_age_s=None if self.last_abort_at is None else round(now - self.last_abort_at, 2),
                          recording=None if self.record is None else {
                              "path": str(self.record["folder"]), "bytes": self.record["bytes"]},
                          last_recording=self.record_result,
                          reference_frame=self.pipeline.reference_frame,
                          registers=self.register_state())
            if since != self.version:
                result["frame"] = self.latest
            return result

    def disconnect(self):
        with self.lifecycle:
            self._disconnect()

    def _disconnect(self):
        self.stop_event.set()
        for thread in self.threads:
            thread.join(timeout=5)
        if any(t.is_alive() for t in self.threads):
            raise RuntimeError("Acquisition worker did not stop; refusing to start another source")
        self.threads = []
        if self.transport is not None:
            self.transport.close()
            self.transport = None
        with self.lock:
            self._stop_recording()
            self.status = "disconnected"

    def connect(self, port=None, replay=None):
        with self.lifecycle:
            self._disconnect()
            if replay is None:
                ports = usb_ports()
                port = port or (ports[0] if len(ports) == 1 else None)
                if port not in ports:
                    raise ValueError("Select the LD2450 native USB port; no matching device is available")
                # A write timeout keeps firmware that never reads commands from hanging the server.
                transport = serial.Serial(port=None, baudrate=115200, timeout=.1, write_timeout=1,
                                          rtscts=False, dsrdtr=False)
                transport.port = port
                transport.dtr = True
                try:
                    transport.open()
                    transport.dtr = True
                except Exception:
                    transport.close()
                    raise
                self.transport = transport
                # The first OUT packet after opening is lost on this device; absorb it
                # with one byte the command parser discards.
                transport.write(b"\0")
                source = "USB " + port
            else:
                replay = Path(replay).resolve(strict=True)
                source = "Replay: " + replay.parent.name
            self.stop_event = threading.Event()
            with self.pipeline_lock:
                self.pipeline.clear_reference()
            with self.lock:
                self.reset_stats()
                self.reset_registers()
                self.latest = self.raw_frame = None
                self.last_frame_at = None
                self.version += 1
                self.generation += 1
                self.status, self.source, self.error = "replay" if replay else "live", source, ""
            frame_queue = queue.Queue(maxsize=1)
            processor = threading.Thread(target=self._process, args=(frame_queue,), daemon=True, name="radar-dsp")
            self.threads = [processor]
            if replay is not None:
                self.threads.append(threading.Thread(target=self._replay, args=(replay, frame_queue),
                                                     daemon=True, name="radar-replay"))
            else:
                chunks = queue.Queue(maxsize=64)  # At most 4 MiB of pending transport bytes.
                self.threads += [threading.Thread(target=self._decode, args=(chunks, frame_queue),
                                                  daemon=True, name="radar-decoder"),
                                 threading.Thread(target=self._send_commands, args=(self.commands,),
                                                  daemon=True, name="radar-commands"),
                                 threading.Thread(target=self._read_usb, args=(chunks,),
                                                  daemon=True, name="radar-usb")]
            for thread in self.threads:
                thread.start()

    def fail(self, exc):
        with self.lock:
            self.error, self.status = str(exc), "error"
        self.stop_event.set()

    def _read_usb(self, chunks):
        try:
            while not self.stop_event.is_set():
                data = self.transport.read(max(4096, min(self.transport.in_waiting, 65536)))
                if not data:
                    continue
                with self.lock:
                    self.stats["received_bytes"] += len(data)
                    if self.record is not None:
                        self.record["file"].write(data)
                        self.record["hash"].update(data)
                        self.record["bytes"] += len(data)
                        if self.record["bytes"] >= RECORD_LIMIT:
                            self._stop_recording("1 GiB recording limit reached")
                try:
                    chunks.put_nowait(data)
                except queue.Full:
                    raise RuntimeError("Host decoder backlog exceeded 4 MiB; stream stopped. Reconnect to recover.")
        except Exception as exc:
            self.fail(exc)
        finally:
            self.transport.close()
            with self.lock:
                self._stop_recording()

    def _update_decode(self, parser, frames):
        with self.lock:
            if frames.aborted != self.stats["device_aborts"]:
                self.last_abort_at = time.monotonic() if frames.last_abort else None
            self.stats.update(parser_errors=parser.errors, discarded_bytes=parser.discarded_bytes,
                              protocol_errors=frames.protocol_errors, rejected_frames=frames.rejected,
                              device_aborts=frames.aborted, queue_aborts=frames.abort_reasons.get(3, 0),
                              cpu_aborts=frames.abort_reasons.get(6, 0),
                              other_aborts=sum(v for k, v in frames.abort_reasons.items() if k not in (3, 6)),
                              invalid_frames=frames.rejected - frames.aborted, last_abort=frames.last_abort)
            # BEGIN telemetry remains current even if every candidate aborts.
            self.stats.update(frames.latest_device_stats)
            elapsed = time.monotonic() - self.rate_at
            if elapsed >= 1:
                self.stats["wire_kbps"] = round((self.stats["received_bytes"] - self.rate_bytes) / elapsed / 1000, 1)
                self.stats["frames_per_second"] = round((self.stats["complete_frames"] - self.rate_frames) / elapsed, 1)
                self.rate_bytes, self.rate_frames = self.stats["received_bytes"], self.stats["complete_frames"]
                self.rate_at = time.monotonic()

    def _accept_replies(self, frames):
        while frames.replies:
            reply = frames.replies.popleft()
            with self.lock:
                request = self.pending.pop(reply["tag"], None)
                self.register_generation = reply["generation"]
                for n, value in enumerate(reply["values"]):
                    self.registers[(reply["register"] + n) & 255] = dict(
                        value=value, op="read" if reply["op"] == CONTROL_READ else "write",
                        ok=reply["status"] == 0, generation=reply["generation"], at=time.time())
                if reply["op"] == CONTROL_REINIT and reply["status"] == 0:
                    self.registers = {}  # Build profile re-applied: earlier readings are stale.
                self.register_log.append(dict(
                    at=time.time(), tag=reply["tag"], op=reply["op"], register=reply["register"],
                    values=reply["values"], status=CONTROL_STATUS.get(reply["status"], str(reply["status"])),
                    driver_error=reply["driver_error"], generation=reply["generation"],
                    attempts=None if request is None else request.get("attempts"),
                    latency_s=None if request is None or request["sent"] is None
                    else round(time.monotonic() - request["sent"], 3)))

    def send_command(self, op, register=0, count=0, value=0):
        """Queue one LDC1 command for the live USB device; returns its tag."""
        with self.lock:
            if self.status != "live" or self.transport is None:
                raise ValueError("Register control needs a live USB connection")
            tag = self.next_tag
            self.next_tag += 1
            self.pending[tag] = dict(op=op, register=register, count=count, value=value, sent=None)
            commands = self.commands
        commands.put(tag)
        return tag

    def _send_commands(self, commands):
        """Send queued commands one at a time, waiting for each reply."""
        while not self.stop_event.is_set():
            try:
                tag = commands.get(timeout=.1)
            except queue.Empty:
                continue
            with self.lock:
                request = self.pending.get(tag)
                transport = self.transport
            if request is None or transport is None:
                continue
            reinit = request["op"] == CONTROL_REINIT
            packet = encode_command(request["op"], request["register"], request["count"], request["value"], tag)
            for attempt in range(1 if reinit else COMMAND_ATTEMPTS):
                with self.lock:
                    request["sent"] = time.monotonic()
                    request["attempts"] = attempt + 1
                try:
                    with self.write_lock:
                        transport.write(packet)
                except (serial.SerialTimeoutException, serial.SerialException) as exc:
                    with self.lock:
                        self.pending.pop(tag, None)
                        self.register_log.append(dict(
                            at=time.time(), tag=tag, op=request["op"], register=request["register"], values=[],
                            status="not accepted by device (register-control firmware installed?)",
                            driver_error=0, generation=self.register_generation, latency_s=None))
                    if isinstance(exc, serial.SerialTimeoutException):
                        break
                    return
                deadline = time.monotonic() + (REINIT_TIMEOUT_S if reinit else REPLY_TIMEOUT_S)
                while time.monotonic() < deadline and not self.stop_event.is_set():
                    with self.lock:
                        if tag not in self.pending:
                            break
                    time.sleep(.01)
                with self.lock:
                    if tag not in self.pending:
                        break

    def register_read(self, register, count):
        if not (0 <= register <= 255 and 1 <= count and register + count <= 256):
            raise ValueError("Register range must lie within 0x00-0xFF")
        return [self.send_command(CONTROL_READ, r, min(READ_CHUNK, register + count - r))
                for r in range(register, register + count, READ_CHUNK)]

    def register_write(self, register, value):
        if not (0 <= register <= 255 and 0 <= value <= 0xFFFF):
            raise ValueError("Register 0x00-0xFF and value 0x0000-0xFFFF required")
        return [self.send_command(CONTROL_WRITE, register, 1, value)]

    def register_reinit(self):
        return [self.send_command(CONTROL_REINIT)]

    def register_state(self):
        now = time.monotonic()
        with self.lock:
            def waiting(p):
                limit = REINIT_TIMEOUT_S if p["op"] == CONTROL_REINIT else REPLY_TIMEOUT_S
                return p["sent"] is None or now - p["sent"] < limit or p.get("attempts", 1) < COMMAND_ATTEMPTS
            return dict(
                generation=self.register_generation,
                values={f"{r:02x}": v for r, v in sorted(self.registers.items())},
                pending=sum(waiting(p) for p in self.pending.values()),
                timed_out=sum(not waiting(p) for p in self.pending.values()),
                log=list(self.register_log)[-40:])

    def _publish_raw(self, frame, frame_queue):
        # Settings identity: build configuration plus live register generation.
        frame["config_id"] = f'{frame["config_sha256"]}:{frame.get("register_generation", 0)}'
        with self.lock:
            self.raw_frame = frame
            self.stats["complete_frames"] += 1
            for key in ("device_skipped", "device_rejected", "device_queue_peak"):
                self.stats[key] = frame[key]
        try:
            frame_queue.put_nowait(frame)
        except queue.Full:
            try:
                frame_queue.get_nowait()
                with self.lock:
                    self.stats["processing_drops"] += 1
            except queue.Empty:
                pass
            frame_queue.put_nowait(frame)

    def _decode(self, chunks, frame_queue):
        parser, frames = Parser(), Frames()
        try:
            while not self.stop_event.is_set():
                try:
                    data = chunks.get(timeout=.1)
                except queue.Empty:
                    continue
                for message in parser.feed(data):
                    frame = frames.accept(message)
                    if frame is not None:
                        self._publish_raw(frame, frame_queue)
                self._accept_replies(frames)
                self._update_decode(parser, frames)
        except Exception as exc:
            self.fail(exc)

    def _replay(self, path, frame_queue):
        try:
            while not self.stop_event.is_set():
                parser, frames = Parser(), Frames()
                previous = None
                due_at = time.monotonic()
                count = 0
                with path.open("rb") as stream:
                    while not self.stop_event.is_set():
                        data = stream.read(32768)
                        if not data:
                            break
                        with self.lock:
                            self.stats["received_bytes"] += len(data)
                        for message in parser.feed(data):
                            frame = frames.accept(message)
                            if frame is not None:
                                if previous is not None:
                                    delta = ((frame["started_us"] - previous) & 0xffffffff) / 1e6
                                    due_at += min(delta, 2)
                                    if self.stop_event.wait(max(0, due_at - time.monotonic())):
                                        return
                                previous = frame["started_us"]
                                self._publish_raw(frame, frame_queue)
                                count += 1
                        self._accept_replies(frames)
                        self._update_decode(parser, frames)
                if self.stop_event.is_set():
                    return
                with self.lock:
                    self.stats["truncated_tail"] = bool(parser.buffer or frames.current)
                if not count:
                    raise ValueError("Replay contains no complete, validated frames")
                # A source boundary discards the partial tail and clears display history.
                if self.stop_event.wait(.3):
                    return
                with self.pipeline_lock:
                    self.pipeline.clear_reference()
                with self.lock:
                    self.generation += 1
                    self.stats["replay_loops"] += 1
        except Exception as exc:
            self.fail(exc)

    def _process(self, frame_queue):
        while not self.stop_event.is_set():
            try:
                frame = frame_queue.get(timeout=.1)
            except queue.Empty:
                continue
            try:
                with self.pipeline_lock:
                    with self.lock:
                        settings = dict(self.settings)
                    result = self.pipeline.process(frame, settings)
                    with self.lock:
                        if self.latest and self.latest["config_id"] != result["config_id"]:
                            self.generation += 1
                        result["generation"] = self.generation
                        self.latest = result
                        self.last_frame_at = time.monotonic()
                        self.version += 1
                        self.stats["timing_outliers"] += result["products"].get("quality", {}).get("timing_outliers", 0)
            except Exception as exc:
                self.fail(exc)

    def set_settings(self, values):
        values = validate_settings(values)
        with self.pipeline_lock, self.lock:
            self.settings = values
            self.generation += 1

    def iq_calibration(self, enabled):
        """Fit I/Q gain/phase correction from the latest raw frame, or clear it."""
        with self.pipeline_lock, self.lock:
            if enabled:
                if self.raw_frame is None:
                    raise ValueError("Wait for a complete frame before calibrating I/Q")
                summary = self.pipeline.set_iq_calibration(self.raw_frame)
            else:
                self.pipeline.clear_iq_calibration()
                summary = None
            self.generation += 1
            return summary

    def reference(self, enabled):
        with self.pipeline_lock, self.lock:
            if enabled:
                if self.raw_frame is None:
                    raise ValueError("Wait for a complete frame before capturing a reference")
                self.pipeline.set_reference(self.raw_frame)
            else:
                self.pipeline.clear_reference()
            self.generation += 1

    def start_recording(self):
        with self.lock:
            if self.status != "live":
                raise ValueError("Raw recording is available during live USB acquisition")
            if self.record is not None:
                return
            folder = new_folder("capture")
            self.record = dict(folder=folder, file=(folder / "stream.ldf").open("xb"),
                               hash=hashlib.sha256(), bytes=0, source=self.source,
                               started=datetime.now().astimezone().isoformat())

    def _stop_recording(self, reason="Stopped by user or source closed"):
        if self.record is None:
            return
        record, self.record = self.record, None
        record["file"].close()
        report = dict(source=record["source"], received_bytes=record["bytes"],
                      started=record["started"], stream_sha256=record["hash"].hexdigest(),
                      reason=reason, note="Unmodified wire bytes; start/end may contain partial frames.")
        (record["folder"] / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        self.record_result = str(record["folder"])
        self.sources = self.discover_sources()

    def stop_recording(self):
        with self.lock:
            self._stop_recording()

    def snapshot(self):
        with self.lock:
            if self.raw_frame is None:
                raise ValueError("No complete frame available")
            frame = dict(self.raw_frame)
            metadata = dict(source=self.source, settings=dict(self.settings),
                            reference_frame=self.pipeline.reference_frame)
        folder = new_folder("snapshot")
        save_frame(frame, folder, 1)
        (folder / "viewer.json").write_text(json.dumps(metadata, indent=2) + "\n")
        return str(folder)


def make_handler(viewer, token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def respond(self, status, body, content_type="application/json"):
            if not isinstance(body, bytes):
                body = json.dumps(body, allow_nan=False, separators=(",", ":")).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def valid_host(self):
            return self.headers.get("Host") in (f"127.0.0.1:{self.server.server_port}",
                                                 f"localhost:{self.server.server_port}")

        def do_GET(self):
            if not self.valid_host():
                return self.respond(403, {"error": "Loopback host required"})
            parsed = urlparse(self.path)
            try:
                if parsed.path == "/api/state":
                    return self.respond(200, viewer.state(int(parse_qs(parsed.query).get("since", [-1])[0])))
                if parsed.path == "/api/options":
                    with viewer.lock:
                        sources = [{"id": key, "name": str(path.relative_to(ROOT))} for key, path in viewer.sources.items()]
                    notes = {f"{r:02x}": n for r, n in sorted(viewer.notes.items())}
                    return self.respond(200, {"ports": usb_ports(), "sources": sources, "token": token,
                                              "register_notes": notes})
                static = {"/": ("index.html", "text/html; charset=utf-8"),
                          "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                          "/style.css": ("style.css", "text/css; charset=utf-8")}
                if parsed.path in static:
                    name, mime = static[parsed.path]
                    return self.respond(200, (WEB / name).read_bytes(), mime)
                return self.respond(404, {"error": "Not found"})
            except (ValueError, OSError) as exc:
                return self.respond(400, {"error": str(exc)})

        def do_POST(self):
            # Drain small request bodies before rejecting authentication. Closing
            # with unread input can reset the socket on Windows, hiding the 403.
            try:
                length = int(self.headers.get("Content-Length", 0))
                if not 0 <= length <= 4096:
                    raise ValueError("Request too large")
                body = self.rfile.read(length)
            except ValueError as exc:
                return self.respond(400, {"error": str(exc)})
            origin = self.headers.get("Origin")
            allowed_origins = (f"http://127.0.0.1:{self.server.server_port}", f"http://localhost:{self.server.server_port}")
            if (not self.valid_host() or self.headers.get("X-Viewer-Token") != token
                    or (origin is not None and origin not in allowed_origins)):
                return self.respond(403, {"error": "Local viewer token and origin required"})
            try:
                data = json.loads(body or b"{}")
                if not isinstance(data, dict):
                    raise ValueError("Expected JSON object")
                if self.path == "/api/connect":
                    viewer.connect(port=data.get("port"))
                elif self.path == "/api/replay":
                    with viewer.lock:
                        path = viewer.sources.get(data.get("id"))
                    if path is None:
                        raise ValueError("Unknown recording")
                    viewer.connect(replay=path)
                elif self.path == "/api/disconnect":
                    viewer.disconnect()
                elif self.path == "/api/settings":
                    viewer.set_settings(data)
                elif self.path == "/api/iq-calibration":
                    if type(data.get("enabled")) is not bool:
                        raise ValueError("enabled must be boolean")
                    return self.respond(200, {"calibration": viewer.iq_calibration(data["enabled"])})
                elif self.path == "/api/reference":
                    if type(data.get("enabled")) is not bool:
                        raise ValueError("enabled must be boolean")
                    viewer.reference(data["enabled"])
                elif self.path == "/api/record/start":
                    viewer.start_recording()
                elif self.path == "/api/record/stop":
                    viewer.stop_recording()
                elif self.path == "/api/register/read":
                    tags = viewer.register_read(int(data["register"]), int(data.get("count", 1)))
                    return self.respond(200, {"tags": tags})
                elif self.path == "/api/register/write":
                    return self.respond(200, {"tags": viewer.register_write(int(data["register"]), int(data["value"]))})
                elif self.path == "/api/register/reinit":
                    return self.respond(200, {"tags": viewer.register_reinit()})
                elif self.path == "/api/snapshot":
                    return self.respond(200, {"path": viewer.snapshot()})
                else:
                    return self.respond(404, {"error": "Not found"})
                return self.respond(200, {"ok": True})
            except (ValueError, OSError, RuntimeError, KeyError, TypeError) as exc:
                return self.respond(400, {"error": str(exc)})
    return Handler


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8765, help="Loopback HTTP port")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--connect", action="store_true", help="Open the matching native USB device with DTR asserted")
    group.add_argument("--replay", type=Path, help="Replay a saved LDF1 stream in a loop")
    args = ap.parse_args()
    viewer = Viewer()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(viewer, secrets.token_urlsafe(32)))
    server.daemon_threads = True
    try:
        if args.connect or args.replay:
            try:
                viewer.connect(replay=args.replay)
            except (OSError, ValueError) as exc:
                viewer.error = str(exc)
        print(f"Radar viewer: http://127.0.0.1:{server.server_port}", flush=True)
        server.serve_forever(poll_interval=.2)
    except KeyboardInterrupt:
        pass
    finally:
        viewer.disconnect()
        server.server_close()

