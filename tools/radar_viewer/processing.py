"""Range-bin processing for the live viewer; axes stay uncalibrated.

Every frame is handled as range bins: the unwindowed, unscaled FFT bins -K..K
of each chirp. Range-bin frames (LDF1 codec 2) arrive that way from the device's
hardware FFT. Raw frames (older images and recordings) are converted on the host
with the same transform (512-point FFT, K = RAW_BINS_HALF), so one pipeline
serves both.

DC removal, background subtraction, I/Q correction and the Hann window are
exact bin-domain operations. The Hann window combines neighbouring bins, so the
published spectra cover bins -(K-1)..(K-1). Views that need time samples
(waveform, within-chirp spectrogram, linear-trend removal) were removed when
the device moved to range-bin export.

Target detection and angle (stage "targets") run on the range-Doppler map:
CFAR over the summed receiver power, local maxima, merging of nearby cells,
sub-bin interpolation, then the RX2-RX1 phase at each target for its angle.
Calibration values (range scale, wavelength, antenna spacing, phase offset,
signs, detection parameters) come from calibration.json. Stage "tracks" follows
objects across frames (Tracker): consistency over time, not agreement between
the two receivers, is what separates real objects from noise here; summing both
receivers' power is already the best two-channel detector for an unknown angle.

Add a stage to Pipeline.stages to publish another named product. Each stage
receives a FrameContext and returns JSON-compatible data. Acquisition and the
LDF1 integrity boundary do not need to change when adding a stage.
"""
from dataclasses import dataclass, field
import base64
import json
from pathlib import Path
import time

import numpy as np


DEFAULT_SETTINGS = {"remove_dc": True, "window": "hann", "remove_static": True}
CHANGE_ALPHA = 0.1   # Running-average weight per processed frame (about 10-frame memory).
RAW_BINS_HALF = 40   # Raw frames are reduced to the same bins the device exports.
MIRROR_BINS = np.arange(2, 13)  # Signed FFT bins where the scene dominates the noise.
CALIBRATION_PATH = Path(__file__).with_name("calibration.json")


def load_calibration(path=CALIBRATION_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate_settings(values):
    if set(values) != set(DEFAULT_SETTINGS):
        raise ValueError("Settings must contain remove_dc, window and remove_static")
    if any(type(values[key]) is not bool for key in ("remove_dc", "remove_static")):
        raise ValueError("DC and static removal must be booleans")
    if values["window"] not in ("hann", "rectangular"):
        raise ValueError("Unknown window")
    return dict(values)


def unpack_iq(frame):
    """Raw frame -> receivers x chirps x samples x (I, Q) int16."""
    chirps, pairs = frame.get("chirps", 64), frame.get("pairs", 512)
    if chirps not in (16, 64) or any(len(lane) != chirps * (8 + 4 * pairs) for lane in frame["lanes"]):
        raise ValueError("Invalid complete export window")
    return np.stack([
        np.frombuffer(lane, dtype=">i2").reshape(chirps, 4 + 2 * pairs)[:, 2:-2].reshape(chirps, pairs, 2)
        for lane in frame["lanes"]
    ]).astype("<i2")


def unpack_bins(frame):
    """Range-bin frame -> complex receivers x chirps x bins (-K..K), unscaled DFT units."""
    chirps, half = frame.get("chirps", 64), frame.get("bins_half") or 0
    width = 2 * half + 1
    if chirps not in (16, 64) or half < 1 or any(len(lane) != chirps * width * 8 for lane in frame["lanes"]):
        raise ValueError("Invalid complete range-bin frame")
    values = np.stack([np.frombuffer(lane, dtype="<i4").reshape(chirps, width, 2)
                       for lane in frame["lanes"]]).astype(np.float64)
    return values[..., 0] + 1j * values[..., 1]


def frame_bins(frame):
    """(bins -K..K, FFT points, source) for either frame format."""
    if frame.get("codec_version") == 2:
        return unpack_bins(frame), frame["pairs"], "device"
    iq = unpack_iq(frame).astype(np.float64)
    points = iq.shape[2]
    ks = np.arange(-RAW_BINS_HALF, RAW_BINS_HALF + 1)
    return np.fft.fft(iq[..., 0] + 1j * iq[..., 1], axis=-1)[..., ks % points], points, "host"


def window_bins(bins, hann, points):
    """Window unwindowed DFT bins -K..K in the bin domain; returns bins -(K-1)..(K-1).

    Periodic Hann is w = 0.5 - 0.5 cos(2 pi n / N), so the windowed DFT is
    0.5 X[k] - 0.25 X[k-1] - 0.25 X[k+1]. Normalised by the window sum (N/2 or N):
    a full-scale tone of amplitude A reads A.
    """
    if hann:
        return (0.5 * bins[..., 1:-1] - 0.25 * bins[..., :-2] - 0.25 * bins[..., 2:]) / (points / 2)
    return bins[..., 1:-1] / points


def iq_correct_bins(bins, gain, phase):
    """Bin-domain form of Q_ideal = (Q/g - I sin(phi)) / cos(phi), per receiver.

    In time samples the correction is A x + B conj(x); the DFT of conj(x) at bin k
    is conj(X[-k]). Bins are in -K..K order, so reversing them maps k to -k.
    """
    t, c = np.tan(phase), np.cos(phase)
    a = (1 - 1j * t) / 2 + 1 / (2 * gain * c)
    b = (1 - 1j * t) / 2 - 1 / (2 * gain * c)
    return a[:, None, None] * bins + b[:, None, None] * np.conj(bins[..., ::-1])


def db(value):
    return np.round(20 * np.log10(np.maximum(value, 1e-6)), 2).tolist()


@dataclass
class FrameContext:
    frame: dict
    raw: np.ndarray       # bins -K..K as received (or host-converted), unscaled
    signal: np.ndarray    # after background, I/Q correction and DC removal, unwindowed
    spectra: np.ndarray   # windowed and normalised, bins -(K-1)..(K-1)
    settings: dict
    chirp_interval_s: float
    points: int
    iq_correction: dict = None
    cache: dict = field(default_factory=dict)

    @property
    def bin_lo(self):
        return -((self.spectra.shape[-1] - 1) // 2)

    def bin_range(self):
        return [self.bin_lo, -self.bin_lo]


def signal_quality(ctx):
    """Chirp-to-chirp variation within the exported band (DC excluded), via Parseval."""
    centered = ctx.raw.copy()
    centered[..., centered.shape[-1] // 2] = 0
    residual = centered - centered.mean(axis=1, keepdims=True)
    rms = np.sqrt(np.sum(abs(centered) ** 2, axis=2).mean(axis=1)) / ctx.points
    residual_rms = np.sqrt(np.sum(abs(residual) ** 2, axis=2).mean(axis=1)) / ctx.points
    intervals = (np.diff(np.asarray(ctx.frame["timestamps_us"], dtype=np.int64), axis=1)
                 & 0xffffffff)
    median = float(np.median(intervals))
    return {
        "ac_rms": np.round(rms, 2).tolist(),
        "residual_rms": np.round(residual_rms, 2).tolist(),
        "residual_percent": np.round(100 * residual_rms / np.maximum(rms, 1e-9), 2).tolist(),
        "chirp_interval_us": median,
        "timing_outliers": int(np.count_nonzero(abs(intervals - median) > median * .1)),
    }


def mirror_factor(bins, points):
    """Mirror-image factor per receiver from a static scene.

    bins: receivers x (2K+1) coherent mean over chirps (-K..K, unwindowed).
    After DC removal and a Hann window, fits X(-k) = alpha * conj(X(k)) over
    MIRROR_BINS: I/Q gain and phase mismatch put a scaled, conjugated copy of
    every positive-frequency component at the matching negative frequency.
    Returns alpha (complex, per receiver), the unexplained fraction of the
    negative-bin energy, and the positive-bin level in dB.
    """
    half = (bins.shape[-1] - 1) // 2
    if half - 1 < MIRROR_BINS[-1]:
        raise ValueError("The I/Q mirror fit needs K >= 13")
    zeroed = bins.copy()
    zeroed[..., half] = 0
    X, zero = window_bins(zeroed, True, points), half - 1
    pos, neg = X[..., zero + MIRROR_BINS], X[..., zero - MIRROR_BINS]
    power = np.sum(np.abs(pos) ** 2, axis=-1)
    alpha = np.sum(neg * pos, axis=-1) / np.maximum(power, 1e-12)
    residual = (np.sum(np.abs(neg - alpha[..., None] * np.conj(pos)) ** 2, axis=-1)
                / np.maximum(np.sum(np.abs(neg) ** 2, axis=-1), 1e-12))
    return alpha, residual, 10 * np.log10(np.maximum(power, 1e-12))


def iq_correction(alpha):
    """Gain g and phase error phi (radians) of Q relative to I, from alpha.

    Model: I = cos(t), Q = g*sin(t + phi), giving alpha = (1 - u)/(1 + u) with
    u = g*exp(-j*phi). Bench-checked: predicted the 0x65 gain-step effects to
    0.1 dB (DEBUG_LOG.md 2026-10-06).
    """
    u = (1 - alpha) / (1 + alpha)
    return np.abs(u), -np.angle(u)


def iq_balance(ctx):
    alpha, residual, level = mirror_factor(ctx.signal.mean(axis=1), ctx.points)
    return {"image_db": np.round(20 * np.log10(np.maximum(abs(alpha), 1e-9)), 2).tolist(),
            "image_deg": np.round(np.degrees(np.angle(alpha)), 1).tolist(),
            "fit_residual": np.round(residual, 3).tolist(), "level_db": np.round(level, 1).tolist(),
            "corrected": ctx.iq_correction is not None,
            "note": "Mirror relative to the scene, bins 2-12 of the coherent mean chirp; needs a static scene"}


def spectrum(ctx):
    return {"db": db(np.sqrt(np.mean(abs(ctx.spectra) ** 2, axis=1))),
            "bins": ctx.bin_range(), "unit": "dB re 1 exported count"}


def range_doppler(ctx):
    """Complex range-Doppler maps (receivers x Doppler x range bins) and Doppler Hz, cached per frame.

    Hann across chirps, fftshifted (Doppler index d is bin d - chirps//2). Optional
    static removal subtracts the within-frame mean before the slow-time FFT.
    """
    if "rd" not in ctx.cache:
        values = ctx.spectra
        if ctx.settings["remove_static"]:
            values = values - values.mean(axis=1, keepdims=True)
        chirps = ctx.spectra.shape[1]
        window = np.hanning(chirps)
        rd = np.fft.fftshift(np.fft.fft(values * window[None, :, None], axis=1), axes=1) / window.sum()
        ctx.cache["rd"] = rd, np.fft.fftshift(np.fft.fftfreq(chirps, ctx.chirp_interval_s))
    return ctx.cache["rd"]


def doppler(ctx):
    transformed, freq = range_doppler(ctx)
    return {"db": db(abs(transformed)), "fast_bins": ctx.bin_range(),
            "hz": np.round(freq, 3).tolist(), "unit": "dB re 1 exported count"}


def box_sum(power, half_range, half_doppler):
    """Sum over a (2*half_doppler+1) x (2*half_range+1) box around every cell.

    The Doppler axis is circular (wraps); range edges reflect.
    """
    p = np.pad(power, ((half_doppler, half_doppler), (0, 0)), mode="wrap")
    p = np.pad(p, ((0, 0), (half_range, half_range)), mode="reflect")
    c = np.pad(p, ((1, 0), (1, 0))).cumsum(axis=0).cumsum(axis=1)
    d, r = power.shape
    hd, hr = 2 * half_doppler + 1, 2 * half_range + 1
    return c[hd:hd + d, hr:hr + r] - c[:d, hr:hr + r] - c[hd:hd + d, :r] + c[:d, :r]


def _vertex(a, b, c):
    """Parabolic peak offset (bins) from three log-power samples, clipped to +/-0.5."""
    den = a - 2 * b + c
    return float(np.clip(0.5 * (a - c) / den, -0.5, 0.5)) if den else 0.0


def targets(ctx, cal):
    """Detect targets on the range-Doppler map and measure range, velocity and angle.

    Cell-averaging CFAR on |RX1|^2 + |RX2|^2 (guard and training cells from the
    calibration file), positive range bins up to max_range_m only (negative bins
    hold the I/Q mirror and leakage), local maxima, strongest-first merging of
    cells within merge_cells. Angle: phase of sum(RX2 * conj(RX1)) over the 3x3
    cells around the peak, minus the boresight offset, gives
    sin(theta) = sign * dphi / (2 pi d/lambda). |sin| > 1 is clipped and flagged.
    """
    rd, freq = range_doppler(ctx)
    det, rng, ang, vel = cal["detection"], cal["range"], cal["angle"], cal["velocity"]
    power = np.sum(np.abs(rd) ** 2, axis=0)
    n_doppler, n_range = power.shape
    (gr, gd), (tr, td) = det["guard_cells"], det["training_cells"]
    outer, inner = box_sum(power, gr + tr, gd + td), box_sum(power, gr, gd)
    count = (2 * (gr + tr) + 1) * (2 * (gd + td) + 1) - (2 * gr + 1) * (2 * gd + 1)
    noise = np.maximum((outer - inner) / count, 1e-30)
    log_power = 10 * np.log10(np.maximum(power, 1e-30))
    snr = log_power - 10 * np.log10(noise)
    bins = np.arange(ctx.bin_lo, ctx.bin_lo + n_range)
    max_bin = (det["max_range_m"] - rng["offset_m"]) / rng["m_per_bin"]
    doppler_bins = np.arange(n_doppler) - n_doppler // 2
    valid = (bins >= 1)[None, :] & (bins <= max_bin)[None, :] & (snr >= det["threshold_db"])
    if ctx.settings["remove_static"]:
        valid &= (np.abs(doppler_bins) >= det["min_doppler_bin"])[:, None]
    valid[:, [0, -1]] = False
    neighbours = np.max([np.roll(np.roll(power, a, axis=0), b, axis=1)
                         for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b], axis=0)
    cells = sorted(zip(*np.nonzero(valid & (power >= neighbours))), key=lambda c: -power[c])
    picked, (mr, md) = [], det["merge_cells"]
    for d, r in cells:
        if any(abs(r - r2) <= mr and min(abs(d - d2), n_doppler - abs(d - d2)) <= md for d2, r2 in picked):
            continue
        picked.append((d, r))
        if len(picked) >= det["max_targets"]:
            break
    bin_hz = 1 / (n_doppler * ctx.chirp_interval_s)
    k_angle = 2 * np.pi * ang["d_over_lambda"]
    found = []
    for d, r in picked:
        rows = [(d + a) % n_doppler for a in (-1, 0, 1)]
        block = rd[:, rows][:, :, r - 1:r + 2]
        cross = np.sum(block[1] * np.conj(block[0]))
        coherence = abs(cross) / np.sqrt(np.sum(abs(block[0]) ** 2) * np.sum(abs(block[1]) ** 2))
        dphi = np.angle(cross * np.exp(-1j * np.radians(ang["phase_offset_deg"])))
        sine = ang["sign"] * dphi / k_angle
        theta = float(np.degrees(np.arcsin(np.clip(sine, -1, 1))))
        k = bins[r] + _vertex(log_power[d, r - 1], log_power[d, r], log_power[d, r + 1])
        f = freq[d] + bin_hz * _vertex(log_power[rows[0], r], log_power[d, r], log_power[rows[2], r])
        range_m = rng["m_per_bin"] * k + rng["offset_m"]
        found.append({
            "range_m": round(float(range_m), 3), "angle_deg": round(theta, 1),
            "velocity_mps": round(float(vel["sign"] * f * cal["wavelength_m"] / 2), 3),
            "x_m": round(float(range_m * np.sin(np.radians(theta))), 3),
            "y_m": round(float(range_m * np.cos(np.radians(theta))), 3),
            "snr_db": round(float(snr[d, r]), 1), "power_db": round(float(log_power[d, r]), 1),
            "range_bin": round(float(k), 2), "doppler_hz": round(float(f), 2),
            "phase_deg": round(float(np.degrees(np.angle(cross))), 1),
            "coherence": round(float(coherence), 3), "angle_ambiguous": bool(abs(sine) > 1)})
    ctx.cache["targets"] = found
    return {"targets": found, "threshold_db": det["threshold_db"], "max_range_m": det["max_range_m"],
            "noise_db": round(float(np.median(10 * np.log10(noise))), 1),
            "moving_only": bool(ctx.settings["remove_static"]),
            "calibrated": {"range": rng["calibrated"], "angle": ang["calibrated"], "velocity": vel["calibrated"]},
            "units": {"range": "m", "angle": "deg, positive per calibration sign", "velocity": "m/s"}}


TRACKING_DEFAULTS = {
    "confirm_hits": 3, "confirm_frames": 5, "coast_s": 1.0, "max_gap_s": 1.0, "accel_mps2": 3.0,
    "initial_speed_mps": 1.5, "range_sigma_m": 0.25, "gate_chi2": 13.8, "cluster_range_m": 0.9,
    "cluster_deg": 20.0, "history_s": 3.0, "in_place_min_mps": 0.25, "in_place_ratio": 0.35,
    "coast_velocity_tau_s": 0.5, "max_speed_mps": 3.0, "max_angle_deg": 80.0,
}


def cluster_detections(found, p):
    """One measurement per object: an object (a person's torso and limbs, a fan's blades) often
    gives several Doppler peaks at one place. Strongest first, a detection within cluster_range_m
    and cluster_deg of a cluster's strongest member joins it; the measurement keeps that member's
    position, radial velocity and SNR."""
    clusters = []
    for t in sorted(found, key=lambda t: -t["power_db"]):
        for c in clusters:
            if abs(t["range_m"] - c["range_m"]) <= p["cluster_range_m"] and abs(t["angle_deg"] - c["angle_deg"]) <= p["cluster_deg"]:
                c["members"] += 1
                break
        else:
            clusters.append(dict(t, members=1))
    return clusters


def measurement(m, p):
    """Position measurement (x, y) and its covariance from range and angle.

    Range sigma is fixed; the angle sigma follows the RX2-RX1 phase-difference error for the
    detection's SNR, sigma_phi ~ 1/sqrt(SNR), mapped through sin(theta) = phi / (2 pi d/lambda)
    (d/lambda = 0.5 assumed here), between 2 and 20 degrees."""
    r, th = m["range_m"], np.radians(m["angle_deg"])
    snr = 10 ** (m["snr_db"] / 10)
    s_th = float(np.clip(1 / (np.pi * max(np.cos(th), .2) * np.sqrt(snr / 2)), np.radians(2), np.radians(20)))
    J = np.array([[np.sin(th), r * np.cos(th)], [np.cos(th), -r * np.sin(th)]])
    return np.array([m["x_m"], m["y_m"]]), J @ np.diag([p["range_sigma_m"] ** 2, s_th ** 2]) @ J.T


class Tracker:
    """Constant-velocity Kalman tracks in x, y across frames.

    A detection is one frame's noisy evidence; an object that is really there reappears at a
    consistent place in later frames, noise does not. Tracks start tentative and are confirmed
    after confirm_hits detections within confirm_frames frames; a confirmed track coasts on its
    prediction through missed frames for up to coast_s. Association is greedy nearest-first by
    Mahalanobis distance within gate_chi2. Velocity comes from positions; Doppler radial velocity
    is kept separately so the two can be compared: an object whose Doppler says it moves but whose
    range does not change (a fan, a fidgeting hand) is flagged in_place.
    Time comes from frame start stamps; a gap over max_gap_s or a stamp going backwards
    (replay restart) clears all tracks.
    """

    def __init__(self):
        self.next_id = 1   # Never reused, so a restart cannot relabel an old track.
        self.reset()

    def reset(self):
        self.tracks, self.last_us, self.time = [], None, 0.0

    def update(self, found, t_us, cal):
        p = dict(TRACKING_DEFAULTS, **cal.get("tracking", {}))
        dt = None if self.last_us is None else ((t_us - self.last_us) & 0xffffffff) / 1e6
        if dt is None or dt > p["max_gap_s"]:
            self.reset()
            dt = 0.0
        self.last_us = t_us
        self.time += dt
        F = np.eye(4)
        F[0, 2] = F[1, 3] = dt
        g = np.array([[dt ** 2 / 2, 0], [0, dt ** 2 / 2], [dt, 0], [0, dt]])
        Q = p["accel_mps2"] ** 2 * g @ g.T
        H = np.eye(2, 4)
        for tr in self.tracks:
            tr["x"], tr["P"] = F @ tr["x"], F @ tr["P"] @ F.T + Q
        meas = cluster_detections(found, p)
        zs = [measurement(m, p) for m in meas]
        pairs = []
        for i, tr in enumerate(self.tracks):
            for j, (z, R) in enumerate(zs):
                nu, S = z - H @ tr["x"], H @ tr["P"] @ H.T + R
                d2 = float(nu @ np.linalg.solve(S, nu))
                if d2 <= p["gate_chi2"]:
                    pairs.append((d2, i, j))
        used_t, used_m = set(), set()
        for d2, i, j in sorted(pairs):
            if i in used_t or j in used_m:
                continue
            used_t.add(i)
            used_m.add(j)
            tr, (z, R), m = self.tracks[i], zs[j], meas[j]
            S = H @ tr["P"] @ H.T + R
            K = tr["P"] @ H.T @ np.linalg.inv(S)
            tr["x"] = tr["x"] + K @ (z - H @ tr["x"])
            tr["P"] = (np.eye(4) - K @ H) @ tr["P"]
            tr.update(last_hit=self.time, snr_db=m["snr_db"], members=m["members"])
            tr["hits"].append((self.time, m["range_m"], m["velocity_mps"]))
        decay = np.exp(-dt / p["coast_velocity_tau_s"])
        for i, tr in enumerate(self.tracks):
            if i not in used_t:   # Coasting: let the velocity die away rather than extrapolate noise.
                tr["x"][2:] *= decay
            speed = np.hypot(*tr["x"][2:])
            if speed > p["max_speed_mps"]:
                tr["x"][2:] *= p["max_speed_mps"] / speed
            tr["recent"] = (tr["recent"] + [i in used_t])[-p["confirm_frames"]:]
            if not tr["confirmed"] and sum(tr["recent"]) >= p["confirm_hits"]:
                tr["confirmed"] = True
        for j, ((z, R), m) in enumerate(zip(zs, meas)):
            if j in used_m:
                continue
            P0 = np.zeros((4, 4))
            P0[:2, :2], P0[2:, 2:] = R, np.eye(2) * p["initial_speed_mps"] ** 2
            self.tracks.append(dict(id=self.next_id, x=np.r_[z, 0.0, 0.0], P=P0, born=self.time,
                                    last_hit=self.time, snr_db=m["snr_db"], members=m["members"],
                                    hits=[(self.time, m["range_m"], m["velocity_mps"])],
                                    recent=[True], confirmed=False, trail=[]))
            self.next_id += 1
        keep = []
        misses_allowed = p["confirm_frames"] - p["confirm_hits"]
        for tr in self.tracks:
            if tr["confirmed"]:
                alive = self.time - tr["last_hit"] <= p["coast_s"]
            else:
                alive = len(tr["recent"]) - sum(tr["recent"]) <= misses_allowed
            x, y = tr["x"][:2]
            if not (y > 0 and abs(np.degrees(np.arctan2(x, y))) <= p["max_angle_deg"]
                    and np.hypot(x, y) <= cal["detection"]["max_range_m"] + 0.5):
                alive = False   # Left the field of view.
            if alive:
                tr["hits"] = [h for h in tr["hits"] if self.time - h[0] <= p["history_s"]]
                tr["trail"] = (tr["trail"] + [(float(tr["x"][0]), float(tr["x"][1]))])[-int(p["history_s"] * 12):]
                keep.append(tr)
        # Two tracks that converge on one object: keep the confirmed, then the older.
        keep.sort(key=lambda tr: (not tr["confirmed"], tr["born"]))
        self.tracks = []
        for tr in keep:
            if not any(np.hypot(*(tr["x"][:2] - o["x"][:2])) < p["cluster_range_m"] / 2 for o in self.tracks):
                self.tracks.append(tr)
        return [self.describe(tr, p) for tr in self.tracks if tr["confirmed"]], len(meas)

    def describe(self, tr, p):
        x, y, vx, vy = (float(v) for v in tr["x"])
        r = float(np.hypot(x, y))
        hits = np.array(tr["hits"])
        rate, in_place = None, False
        if len(hits) >= 5 and hits[-1, 0] - hits[0, 0] >= 1.0:
            rate = float(np.polyfit(hits[:, 0], hits[:, 1], 1)[0])
            doppler_speed = float(np.mean(np.abs(hits[:, 2])))
            in_place = doppler_speed >= p["in_place_min_mps"] and abs(rate) < p["in_place_ratio"] * doppler_speed
        return {"id": tr["id"], "x_m": round(x, 3), "y_m": round(y, 3), "vx_mps": round(vx, 3),
                "vy_mps": round(vy, 3), "range_m": round(r, 3),
                "angle_deg": round(float(np.degrees(np.arctan2(x, y))), 1),
                "speed_mps": round(float(np.hypot(vx, vy)), 3),
                "doppler_mps": round(float(np.mean(hits[-3:, 2])), 3),
                "range_rate_mps": None if rate is None else round(rate, 3),
                "in_place": bool(in_place), "coasting": self.time > tr["last_hit"],
                "age_s": round(self.time - tr["born"], 2), "snr_db": tr["snr_db"], "members": tr["members"],
                "trail": [[round(a, 3), round(b, 3)] for a, b in tr["trail"]]}


class Pipeline:
    def __init__(self, calibration=None):
        self.calibration = load_calibration() if calibration is None else calibration
        self.stages = {"quality": signal_quality, "spectrum": spectrum, "change": self.change,
                       "doppler": doppler, "iq_balance": iq_balance,
                       "targets": lambda ctx: targets(ctx, self.calibration), "tracks": self.track}
        self.tracker, self.tracker_key = Tracker(), None
        self.iq_cal = self.iq_cal_config = None
        self.reference = None
        self.reference_config = None
        self.reference_frame = None
        self.average = self.average_key = None

    def change(self, ctx):
        """Deviation from a running average of the complex spectrum.

        A magnitude spectrum is dominated by static leakage and clutter; motion
        mostly alters phase. Subtracting a slowly updated complex mean exposes it.
        The average restarts whenever configuration, settings or background change.
        """
        key = (ctx.frame.get("config_id", ctx.frame["config_sha256"]), tuple(sorted(ctx.settings.items())),
               self.reference_frame, None if self.iq_cal is None else self.iq_cal["frame_id"], ctx.spectra.shape)
        current = ctx.spectra.mean(axis=1)
        if self.average_key != key:
            self.average, self.average_key = current, key
        deviation = ctx.spectra - self.average[:, None, :]
        self.average = self.average + CHANGE_ALPHA * (current - self.average)
        return {"db": db(np.sqrt(np.mean(abs(deviation) ** 2, axis=1))), "bins": ctx.bin_range(),
                "alpha": CHANGE_ALPHA, "unit": "dB re 1 exported count"}

    def track(self, ctx):
        """Tracks across frames from this frame's detections; restarts when configuration,
        settings or background change."""
        if "targets" not in ctx.cache:
            raise ValueError("No detections this frame")
        key = (ctx.frame.get("config_id", ctx.frame["config_sha256"]), tuple(sorted(ctx.settings.items())),
               self.reference_frame)
        if key != self.tracker_key:
            self.tracker.reset()
            self.tracker_key = key
        tracks, clusters = self.tracker.update(ctx.cache["targets"], ctx.frame["started_us"], self.calibration)
        return {"tracks": tracks, "detections": len(ctx.cache["targets"]), "clusters": clusters,
                "tentative": sum(not tr["confirmed"] for tr in self.tracker.tracks)}

    def set_reference(self, frame):
        self.reference = frame_bins(frame)[0].mean(axis=1, keepdims=True)
        self.reference_config = frame.get("config_id", frame["config_sha256"])
        self.reference_frame = frame["frame_id"]
        self.average = self.average_key = None

    def clear_reference(self):
        self.reference = self.reference_config = self.reference_frame = None
        self.average = self.average_key = None

    def set_iq_calibration(self, frame):
        """Fit per-receiver I/Q gain/phase from a static frame (uncorrected bins)."""
        bins, points, _ = frame_bins(frame)
        alpha, residual, level = mirror_factor(bins.mean(axis=1), points)
        g, phi = iq_correction(alpha)
        self.iq_cal = dict(frame_id=frame["frame_id"], gain=g, phase=phi,
                           summary=dict(frame=frame["frame_id"],
                                        q_gain_db=np.round(20 * np.log10(g), 2).tolist(),
                                        phase_deg=np.round(np.degrees(phi), 1).tolist(),
                                        image_before_db=np.round(20 * np.log10(np.abs(alpha)), 2).tolist(),
                                        fit_residual=np.round(residual, 3).tolist(),
                                        level_db=np.round(level, 1).tolist()))
        self.iq_cal_config = frame.get("config_id", frame["config_sha256"])
        self.average = self.average_key = None
        return self.iq_cal["summary"]

    def clear_iq_calibration(self):
        self.iq_cal = self.iq_cal_config = None
        self.average = self.average_key = None

    def process(self, frame, settings):
        started = time.perf_counter()
        settings = validate_settings(settings)
        config_id = frame.get("config_id", frame["config_sha256"])
        if self.reference is not None and self.reference_config != config_id:
            self.clear_reference()
        if self.iq_cal is not None and self.iq_cal_config != config_id:
            self.clear_iq_calibration()  # Gain registers change the mismatch.
        intervals = np.diff(np.asarray(frame["timestamps_us"], dtype=np.int64), axis=1) & 0xffffffff
        interval_s = float(np.median(intervals)) / 1e6
        if not 0 < interval_s < 1:
            raise ValueError("Invalid chirp interval; cannot form a Doppler frequency axis")
        raw, points, source = frame_bins(frame)
        signal = raw.copy()
        if self.reference is not None and self.reference.shape[-1] == raw.shape[-1]:
            signal -= self.reference
        if self.iq_cal is not None:
            signal = iq_correct_bins(signal, self.iq_cal["gain"], self.iq_cal["phase"])
        if settings["remove_dc"]:
            signal[..., signal.shape[-1] // 2] = 0   # Bin 0 is N times the chirp mean.
        spectra = window_bins(signal, settings["window"] == "hann", points)
        ctx = FrameContext(frame, raw, signal, spectra, settings, interval_s, points,
                           None if self.iq_cal is None else self.iq_cal["summary"])
        products, errors = {}, {}
        for name, stage in self.stages.items():
            try:
                products[name] = stage(ctx)
            except Exception as exc:
                errors[name] = str(exc)
        # Processed, window-normalised bins for per-bin views (constellation).
        values = np.stack([spectra.real, spectra.imag], axis=-1).astype("<f4")
        return {
            "frame_id": frame["frame_id"], "config_sha256": frame["config_sha256"],
            "config_id": config_id, "register_generation": frame.get("register_generation", 0),
            "started_us": frame["started_us"], "settings": settings,
            "reference_frame": self.reference_frame,
            "iq_calibration": None if self.iq_cal is None else self.iq_cal["summary"],
            "chirps": int(spectra.shape[1]), "bin_range": ctx.bin_range(), "fft_points": points,
            "bins_source": source, "bins_shape": list(values.shape), "bins_dtype": "float32-le",
            "bins_base64": base64.b64encode(values.tobytes()).decode("ascii"),
            "products": products, "stage_errors": errors,
            "processing_ms": round((time.perf_counter() - started) * 1000, 2),
        }
