"""Loading and validating PIVOTSBench records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

from . import DIMENSIONS

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
PROMPT_DIR = REPO_ROOT / "prompts"

TASK_FILES = {
    1: "task1_scoring.jsonl",
    2: "task2_keyframe.jsonl",
    3: "task3_causal.jsonl",
}


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records = []
    with open(path, encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no} is not valid JSON: {exc}") from exc
    return records


def load_task(task: int, data_dir: str | Path = DATA_DIR) -> list[dict[str, Any]]:
    """Load one task file. Task 1 records hold six dimensions each."""
    if task not in TASK_FILES:
        raise ValueError(f"task must be 1, 2 or 3, got {task}")
    return load_jsonl(Path(data_dir) / TASK_FILES[task])


def iter_task1_items(
    records: list[dict[str, Any]],
    dimensions: tuple[str, ...] = DIMENSIONS,
    skip_missing: bool = True,
) -> Iterator[dict[str, Any]]:
    """Expand Task 1 records into one benchmark item per (record, dimension).

    This is the unit the paper counts: 765 directional pairs x 6 dimensions.
    """
    for rec in records:
        for dim in dimensions:
            entry = rec["scores"].get(dim)
            if entry is None:
                continue
            if entry.get("score") is None and skip_missing:
                continue
            yield {
                "item_id": f"{rec['item_id']}__{dim}",
                "record_id": rec["item_id"],
                "video": rec["video"],
                "subject": rec["subject"],
                "target": rec["target"],
                "dimension": dim,
                "gold": entry.get("score"),
                "timestamp_sec": entry.get("timestamp_sec"),
                "cues": entry.get("cues", []),
                "rationale": entry.get("rationale"),
            }


def subset_of(record: dict[str, Any]) -> str:
    return record.get("video", {}).get("source", "unknown")
