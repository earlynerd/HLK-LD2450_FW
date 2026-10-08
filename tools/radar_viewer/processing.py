"""Processing stages operate on complete frames; axes stay uncalibrated.

Add a stage to Pipeline.stages to publish another named product. Each stage
receives a FrameContext and returns JSON-compatible data. Acquisition and the
LDF1 integrity boundary do not need to change when adding a stage.
"""
from dataclasses import dataclass
import base64
import time

import numpy as np


DEFAULT_SETTINGS = {"remove_dc": True, "detrend": False, "window": "hann", "remove_static": True}
CHANGE_ALPHA = 0.1  # Running-average weight per processed frame (about 10-frame memory).
STFT_SEGMENT, STFT_HOP, STFT_BINS = 128, 16, 64  # Samples, samples, published signed bins each side.


def validate_settings(values):
    if set(values) != set(DEFAULT_SETTINGS):
        raise ValueError("Settings must contain remove_dc, detrend, window and remove_static")
    if any(type(values[key]) is not bool for key in ("remove_dc", "detrend", "remove_static")):
        raise ValueError("DC, trend and static removal must be booleans")
    if values["window"] not in ("hann", "rectangular"):
        raise ValueError("Unknown window")
    return dict(values)


def unpack_iq(frame):
    chirps, pairs = frame.get('chirps', 64), frame.get('pairs', 512)
    if chirps not in (16, 64) or any(len(lane) != chirps * (8 + 4 * pairs) for lane in frame['lanes']):
        raise ValueError('Invalid complete export window')
    return np.stack([
        np.frombuffer(lane, dtype=">i2").reshape(chirps, 4 + 2 * pairs)[:, 2:-2].reshape(chirps, pairs, 2)
        for lane in frame["lanes"]
    ]).astype("<i2")


def db(value):
    return np.round(20 * np.log10(np.maximum(value, 1e-6)), 2).tolist()


@dataclass
class FrameContext:
    frame: dict
    iq: np.ndarray
    raw: np.ndarray
    signal: np.ndarray
    spectra: np.ndarray
    settings: dict
    chirp_interval_s: float
    iq_correction: dict = None


def signal_quality(ctx):
    centered = ctx.raw - ctx.raw.mean(axis=-1, keepdims=True)
    residual = centered - centered.mean(axis=1, keepdims=True)
    rms = np.sqrt(np.mean(abs(centered) ** 2, axis=(1, 2)))
    residual_rms = np.sqrt(np.mean(abs(residual) ** 2, axis=(1, 2)))
    intervals = (np.diff(np.asarray(ctx.frame["timestamps_us"], dtype=np.int64), axis=1)
                 & 0xffffffff)
    median = float(np.median(intervals))
    return {
        "ac_rms": np.round(rms, 2).tolist(),
        "residual_rms": np.round(residual_rms, 2).tolist(),
        "residual_percent": np.round(100 * residual_rms / np.maximum(rms, 1e-9), 2).tolist(),
        "rail_samples": int(np.count_nonzero((ctx.iq == -32768) | (ctx.iq == 32767))),
        "chirp_interval_us": median,
        "timing_outliers": int(np.count_nonzero(abs(intervals - median) > median * .1)),
    }


MIRROR_BINS = np.arange(2, 13)  # Signed FFT bins where the scene dominates the noise.


def mirror_factor(z):
    """Mirror-image factor per receiver from a static scene.

    z: receivers x 512 complex (one chirp, or a coherent mean over chirps).
    Fits X(-k) = alpha * conj(X(k)) over MIRROR_BINS after DC/drift removal:
    I/Q gain and phase mismatch put a scaled, conjugated copy of every
    positive-frequency component at the matching negative frequency.
    Returns alpha (complex, per receiver), the unexplained fraction of the
    negative-bin energy, and the positive-bin level in dB.
    """
    n = np.arange(z.shape[-1]) - (z.shape[-1] - 1) / 2
    zc = z - z.mean(axis=-1, keepdims=True)
    zc = zc - (zc @ n / (n @ n))[..., None] * n
    w = np.hanning(z.shape[-1])
    X = np.fft.fft(zc * w, axis=-1) / w.sum()
    pos, neg = X[..., MIRROR_BINS], X[..., -MIRROR_BINS]
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
    alpha, residual, level = mirror_factor(ctx.signal.mean(axis=1))
    return {"image_db": np.round(20 * np.log10(np.maximum(abs(alpha), 1e-9)), 2).tolist(),
            "image_deg": np.round(np.degrees(np.angle(alpha)), 1).tolist(),
            "fit_residual": np.round(residual, 3).tolist(), "level_db": np.round(level, 1).tolist(),
            "corrected": ctx.iq_correction is not None,
            "note": "Mirror relative to the scene, bins 2-12 of the coherent mean chirp; needs a static scene"}


def spectrum(ctx):
    return {"db": db(np.sqrt(np.mean(abs(ctx.spectra) ** 2, axis=1))),
            "bins": [-256, 255], "unit": "dB re 1 exported count"}


def doppler(ctx):
    # Full-record fast-time FFT is exploratory until ramp alignment is known.
    values = ctx.spectra[:, :, 192:321]  # Signed fast-time bins -64 through +64.
    if ctx.settings["remove_static"]:
        values = values - values.mean(axis=1, keepdims=True)
    chirps = ctx.iq.shape[1]
    window = np.hanning(chirps)
    transformed = np.fft.fftshift(np.fft.fft(values * window[None, :, None], axis=1), axes=1)
    transformed /= window.sum()
    freq = np.fft.fftshift(np.fft.fftfreq(chirps, ctx.chirp_interval_s))
    return {"db": db(abs(transformed)), "fast_bins": [-64, 64],
            "hz": np.round(freq, 3).tolist(), "unit": "dB re 1 exported count"}


def spectrogram(ctx):
    """Short-time spectrum along each chirp: does a reflector keep one beat frequency?

    A single linear ramp gives a constant beat frequency (a vertical line here);
    segment joins, fold-over or settling appear as jumps or changes along the record.
    Segments are zero-padded to 512 points so bins share the frame spectrum's axis;
    true resolution is 512 / STFT_SEGMENT = 4 bins. RMS over chirps, Hann per segment.
    """
    starts = np.arange(0, 512 - STFT_SEGMENT + 1, STFT_HOP)
    window = np.hanning(STFT_SEGMENT)
    segments = np.stack([ctx.signal[..., a:a + STFT_SEGMENT] for a in starts], axis=2)
    spectra = np.fft.fftshift(np.fft.fft(segments * window, n=512, axis=-1), axes=-1) / window.sum()
    power = np.mean(abs(spectra[..., 256 - STFT_BINS:256 + STFT_BINS + 1]) ** 2, axis=1)
    return {"db": db(np.sqrt(power)), "bins": [-STFT_BINS, STFT_BINS],
            "centers": (starts + STFT_SEGMENT // 2).tolist(), "segment": STFT_SEGMENT,
            "hop": STFT_HOP, "resolution_bins": 512 // STFT_SEGMENT, "unit": "dB re 1 exported count"}


class Pipeline:
    def __init__(self):
        self.stages = {"quality": signal_quality, "spectrum": spectrum, "change": self.change,
                       "doppler": doppler, "spectrogram": spectrogram, "iq_balance": iq_balance}
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
        return {"db": db(np.sqrt(np.mean(abs(deviation) ** 2, axis=1))), "bins": [-256, 255],
                "alpha": CHANGE_ALPHA, "unit": "dB re 1 exported count"}

    def set_reference(self, frame):
        iq = unpack_iq(frame)
        self.reference = (iq[..., 0] + 1j * iq[..., 1]).mean(axis=1, keepdims=True)
        self.reference_config = frame.get("config_id", frame["config_sha256"])
        self.reference_frame = frame["frame_id"]
        self.average = self.average_key = None

    def clear_reference(self):
        self.reference = self.reference_config = self.reference_frame = None
        self.average = self.average_key = None

    def set_iq_calibration(self, frame):
        """Fit per-receiver I/Q gain/phase from a static frame (raw samples, no correction)."""
        iq = unpack_iq(frame)
        alpha, residual, level = mirror_factor((iq[..., 0] + 1j * iq[..., 1]).astype(complex).mean(axis=1))
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
        iq = unpack_iq(frame)
        raw = iq[..., 0].astype(np.float32) + 1j * iq[..., 1].astype(np.float32)
        config_id = frame.get("config_id", frame["config_sha256"])
        if self.reference is not None and self.reference_config != config_id:
            self.clear_reference()
        if self.iq_cal is not None and self.iq_cal_config != config_id:
            self.clear_iq_calibration()  # Gain registers change the mismatch.
        signal = raw.copy()
        if self.reference is not None:
            signal -= self.reference
        if self.iq_cal is not None:
            # Linear: Q_ideal = (Q/g - I*sin(phi)) / cos(phi), per receiver.
            g = self.iq_cal["gain"][:, None, None]
            phi = self.iq_cal["phase"][:, None, None]
            signal = signal.real + 1j * ((signal.imag / g - signal.real * np.sin(phi)) / np.cos(phi))
        if settings["remove_dc"] or settings["detrend"]:
            signal -= signal.mean(axis=-1, keepdims=True)
        if settings["detrend"]:
            # Least-squares straight line per chirp; the slow drift otherwise leaks over the central bins.
            n = np.arange(512) - 255.5
            signal -= (signal @ n / (n @ n))[..., None] * n
        window = np.hanning(512) if settings["window"] == "hann" else np.ones(512)
        spectra = np.fft.fftshift(np.fft.fft(signal * window, axis=-1), axes=-1) / window.sum()
        intervals = np.diff(np.asarray(frame["timestamps_us"], dtype=np.int64), axis=1) & 0xffffffff
        interval_s = float(np.median(intervals)) / 1e6
        if not 0 < interval_s < 1:
            raise ValueError("Invalid chirp interval; cannot form a Doppler frequency axis")
        ctx = FrameContext(frame, iq, raw, signal, spectra, settings, interval_s,
                           None if self.iq_cal is None else self.iq_cal["summary"])
        products, errors = {}, {}
        for name, stage in self.stages.items():
            try:
                products[name] = stage(ctx)
            except Exception as exc:
                errors[name] = str(exc)
        return {
            "frame_id": frame["frame_id"], "config_sha256": frame["config_sha256"],
            "config_id": config_id, "register_generation": frame.get("register_generation", 0),
            "started_us": frame["started_us"], "settings": settings,
            "reference_frame": self.reference_frame,
            "iq_calibration": None if self.iq_cal is None else self.iq_cal["summary"],
            "chirps": int(iq.shape[1]), "iq_shape": list(iq.shape), "iq_dtype": "int16-le",
            "iq_base64": base64.b64encode(iq.tobytes()).decode("ascii"),
            "products": products, "stage_errors": errors,
            "processing_ms": round((time.perf_counter() - started) * 1000, 2),
        }
