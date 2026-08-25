#!/usr/bin/env python3
"""Generate the JSON the project page reads, from the released data files.

The site never hand-copies scores. Drop real records into data/*.jsonl, rerun this,
and docs/ is up to date.

    python scripts/export_site_data.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pivots import CUES, DIMENSIONS  # noqa: E402
from pivots.data import DATA_DIR, load_task  # noqa: E402

DOCS_DATA = ROOT / "docs" / "data"


def build_samples() -> dict:
    meta = json.loads((DATA_DIR / "clip_meta.json").read_text(encoding="utf-8"))["clips"]
    dims = json.loads((DATA_DIR / "schema" / "dimensions.json").read_text(encoding="utf-8"))["dimensions"]

    task1 = load_task(1)
    task2 = load_task(2)
    task3 = load_task(3)

    clips: dict[str, dict] = {}
    for rec in task1:
        video = rec["video"]
        vid = video["video_id"]
        clip = clips.setdefault(vid, {
            "video_id": vid,
            "source": video["source"],
            "youtube_id": video.get("youtube_id"),
            "start_sec": video.get("start_sec", 0),
            "end_sec": video.get("end_sec", 30),
            **{k: v for k, v in meta.get(vid, {}).items()},
            "directions": [],
            "keyframe_items": [],
            "cue_items": [],
        })
        clip["directions"].append({
            "subject": rec["subject"],
            "target": rec["target"],
            "scores": {d: rec["scores"][d] for d in DIMENSIONS},
        })

    for rec in task2:
        vid = rec["video"]["video_id"]
        if vid in clips:
            clips[vid]["keyframe_items"].append({
                "dimension": rec["dimension"],
                "subject": rec["subject"],
                "target": rec["target"],
                "options_sec": rec["options_sec"],
                "answer": rec["answer"],
            })

    for rec in task3:
        vid = rec["video"]["video_id"]
        if vid in clips:
            letters = "ABCDE"
            clips[vid]["cue_items"].append({
                "dimension": rec["dimension"],
                "subject": rec["subject"],
                "target": rec["target"],
                "frame_sec": rec["frame_sec"],
                "options": [CUES[c] for c in rec["options"]],
                "answer": [letters.index(a) for a in rec["answer"]],
                "rationale": rec.get("rationale"),
            })

    return {
        "generated_by": "scripts/export_site_data.py",
        "dimensions": dims,
        "cues": CUES,
        "samples": list(clips.values()),
    }


def main() -> None:
    DOCS_DATA.mkdir(parents=True, exist_ok=True)

    samples = build_samples()
    (DOCS_DATA / "samples.json").write_text(
        json.dumps(samples, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    for name, src in (
        ("leaderboard.json", ROOT / "results" / "paper" / "main_results.json"),
        ("ablations.json", ROOT / "results" / "paper" / "ablations.json"),
        ("stats.json", DATA_DIR / "stats" / "benchmark_stats.json"),
    ):
        (DOCS_DATA / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    n_dir = sum(len(s["directions"]) for s in samples["samples"])
    print(f"wrote {len(samples['samples'])} clips, {n_dir} directions to docs/data/")


if __name__ == "__main__":
    main()
