#!/usr/bin/env python3
"""Validate every data file against its JSON Schema and report what is still missing.

    python scripts/validate_data.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pivots import DIMENSIONS  # noqa: E402
from pivots.data import DATA_DIR, TASK_FILES, load_jsonl  # noqa: E402

SCHEMA_DIR = DATA_DIR / "schema"
SCHEMAS = {
    1: "task1_scoring.schema.json",
    2: "task2_keyframe.schema.json",
    3: "task3_causal.schema.json",
}


def main() -> int:
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        print("jsonschema is not installed: pip install jsonschema")
        return 2

    errors = 0
    for task, filename in TASK_FILES.items():
        path = DATA_DIR / filename
        if not path.exists():
            print(f"missing {path}")
            errors += 1
            continue
        schema = json.loads((SCHEMA_DIR / SCHEMAS[task]).read_text())
        validator = Draft7Validator(schema)
        records = load_jsonl(path)
        seen_ids: set[str] = set()
        for i, rec in enumerate(records, 1):
            for err in validator.iter_errors(rec):
                loc = "/".join(str(p) for p in err.path)
                print(f"{filename}:{i} {loc}: {err.message}")
                errors += 1
            if rec["item_id"] in seen_ids:
                print(f"{filename}:{i} duplicate item_id {rec['item_id']}")
                errors += 1
            seen_ids.add(rec["item_id"])
        print(f"{filename}: {len(records)} records")

    # Coverage of Task 1
    records = load_jsonl(DATA_DIR / TASK_FILES[1])
    pending = [
        f"{r['item_id']}:{d}"
        for r in records
        for d in DIMENSIONS
        if r["scores"][d].get("score") is None
    ]
    filled = len(records) * len(DIMENSIONS) - len(pending)
    print(f"\ntask 1 items scored: {filled}/{len(records) * len(DIMENSIONS)}")
    if pending:
        print("pending: " + ", ".join(pending))

    sources = Counter(r["video"]["source"] for r in records)
    no_id = sum(1 for r in records if not r["video"].get("youtube_id"))
    print(f"records by source: {dict(sources)}")
    print(f"records without a resolvable video identifier: {no_id}")

    print("\nOK" if errors == 0 else f"\n{errors} problem(s) found")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
