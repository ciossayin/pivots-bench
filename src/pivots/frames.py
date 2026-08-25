"""Frame sampling.

The paper samples 8 frames uniformly from each 30-second clip as visual input
(Appendix F.1). Appendix H.3 reports 12- and 15-frame sampling as slightly better,
so N_FRAMES is a parameter rather than a constant.

Task 2 distractors: the ground-truth frame plus offsets of +/-5s and +/-10s. When an
offset falls outside the clip, a different random frame from the same clip is used.
"""

from __future__ import annotations

import base64
import random
from pathlib import Path

N_FRAMES = 8
DISTRACTOR_OFFSETS = (-10.0, -5.0, 5.0, 10.0)


def uniform_timestamps(duration_sec: float, n: int = N_FRAMES) -> list[float]:
    """n timestamps spread over the clip, avoiding the exact first and last frame."""
    if n < 1:
        raise ValueError("n must be >= 1")
    if n == 1:
        return [duration_sec / 2]
    step = duration_sec / (n + 1)
    return [round(step * (i + 1), 3) for i in range(n)]


def distractor_timestamps(
    gold_sec: float,
    duration_sec: float,
    n: int = 4,
    rng: random.Random | None = None,
    min_gap: float = 1.0,
) -> list[float]:
    """Four distractor timestamps for a Task 2 item, following Appendix F.1."""
    rng = rng or random.Random(0)
    out: list[float] = []
    for offset in DISTRACTOR_OFFSETS:
        candidate = gold_sec + offset
        if 0.0 <= candidate <= duration_sec:
            out.append(round(candidate, 3))
    while len(out) < n:
        candidate = round(rng.uniform(0, duration_sec), 3)
        if abs(candidate - gold_sec) >= min_gap and all(abs(candidate - t) >= min_gap for t in out):
            out.append(candidate)
    return out[:n]


def extract_frames(video_path: str | Path, timestamps: list[float]) -> list[bytes]:
    """Decode the given timestamps to JPEG bytes. Requires opencv-python."""
    import cv2  # imported lazily so the metrics path has no heavy dependency

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise FileNotFoundError(f"cannot open video: {video_path}")
    frames = []
    try:
        for ts in timestamps:
            cap.set(cv2.CAP_PROP_POS_MSEC, ts * 1000.0)
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError(f"failed to read frame at {ts}s of {video_path}")
            ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            if not ok:
                raise RuntimeError("JPEG encoding failed")
            frames.append(buf.tobytes())
    finally:
        cap.release()
    return frames


def to_data_url(jpeg_bytes: bytes) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(jpeg_bytes).decode("ascii")
