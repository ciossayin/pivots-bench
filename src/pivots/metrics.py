"""Benchmark metrics.

Task 1 and Task 2 are exact-match accuracy over five options (chance 20%).
Task 3 awards 0.5 for one correct cue and 1.0 for both (chance 40%).
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Sequence

from . import DIMENSIONS


def exact_accuracy(pairs: Iterable[tuple[Any, Any]]) -> float:
    pairs = list(pairs)
    if not pairs:
        return float("nan")
    return 100.0 * sum(1 for gold, pred in pairs if pred is not None and gold == pred) / len(pairs)


def task1_report(items: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """items: dicts with keys 'dimension', 'gold', 'pred'."""
    by_dim: dict[str, list[tuple[Any, Any]]] = defaultdict(list)
    unparsed = 0
    for it in items:
        if it.get("pred") is None:
            unparsed += 1
        by_dim[it["dimension"]].append((it["gold"], it.get("pred")))

    per_dim = {d: exact_accuracy(by_dim[d]) for d in DIMENSIONS if by_dim.get(d)}
    # The paper's Avg is the mean over dimensions, each dimension equally weighted.
    avg = sum(per_dim.values()) / len(per_dim) if per_dim else float("nan")
    return {
        "n_items": len(items),
        "unparsed": unparsed,
        "avg": round(avg, 2),
        "per_dimension": {d: round(v, 2) for d, v in per_dim.items()},
    }


def task2_report(items: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """items: dicts with keys 'answer', 'pred'."""
    acc = exact_accuracy((it["answer"], it.get("pred")) for it in items)
    return {
        "n_items": len(items),
        "unparsed": sum(1 for it in items if it.get("pred") is None),
        "accuracy": round(acc, 2),
    }


def task3_score(gold: Sequence[str], pred: Sequence[str] | None) -> float:
    """0.0, 0.5 or 1.0. Only the first two predicted options count."""
    if not pred:
        return 0.0
    chosen = list(dict.fromkeys(pred))[:2]
    hits = len(set(chosen) & set(gold))
    return {0: 0.0, 1: 0.5, 2: 1.0}[min(hits, 2)]


def task3_report(items: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """items: dicts with keys 'answer' (list of two letters), 'pred'."""
    if not items:
        return {"n_items": 0, "accuracy": float("nan"), "unparsed": 0}
    total = sum(task3_score(it["answer"], it.get("pred")) for it in items)
    return {
        "n_items": len(items),
        "unparsed": sum(1 for it in items if it.get("pred") is None),
        "accuracy": round(100.0 * total / len(items), 2),
        "full_credit_rate": round(
            100.0 * sum(1 for it in items if task3_score(it["answer"], it.get("pred")) == 1.0) / len(items), 2
        ),
    }
