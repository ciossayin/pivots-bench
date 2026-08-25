"""Parsing model output.

Every prompt template asks the model to wrap its answer in ###...###. Models do not
always comply, so each parser falls back to a looser search and reports failures
rather than silently scoring them as wrong.
"""

from __future__ import annotations

import re

from . import SCALE

_WRAPPED = re.compile(r"###\s*(.*?)\s*###", re.S)
_SIGNED_INT = re.compile(r"[-+]?\d")
_VECTOR = re.compile(r"\[\s*(-?\d)\s*(?:,\s*(-?\d)\s*){5}\]")


def _wrapped_payload(text: str) -> str | None:
    matches = _WRAPPED.findall(text or "")
    return matches[-1] if matches else None


def parse_score(text: str, strict: bool = False) -> int | None:
    """Parse a single Likert score from -2 to +2. Returns None if unparseable."""
    payload = _wrapped_payload(text)
    if payload is None:
        if strict:
            return None
        payload = text or ""
    match = re.search(r"[-+]?\s*[0-2]", payload)
    if not match:
        return None
    value = int(match.group().replace(" ", ""))
    return value if value in SCALE else None


def parse_vector(text: str, strict: bool = False) -> list[int] | None:
    """Parse a six-value PIVOTS vector, e.g. ###[-2,1,0,2,1,1]###."""
    payload = _wrapped_payload(text)
    if payload is None:
        if strict:
            return None
        payload = text or ""
    match = re.search(r"\[([^\]]*)\]", payload)
    if not match:
        return None
    values = [int(v) for v in re.findall(r"-?\d+", match.group(1))]
    if len(values) != 6 or any(v not in SCALE for v in values):
        return None
    return values


def parse_vector_pair(text: str) -> tuple[list[int], list[int]] | None:
    """Parse the pairwise setting: ###[...],[...]###."""
    payload = _wrapped_payload(text) or text or ""
    blocks = re.findall(r"\[([^\]]*)\]", payload)
    if len(blocks) < 2:
        return None
    parsed = []
    for block in blocks[:2]:
        values = [int(v) for v in re.findall(r"-?\d+", block)]
        if len(values) != 6 or any(v not in SCALE for v in values):
            return None
        parsed.append(values)
    return parsed[0], parsed[1]


def parse_choice(text: str, n_options: int = 5) -> str | None:
    """Parse a single multiple-choice letter."""
    letters = [chr(ord("A") + i) for i in range(n_options)]
    payload = _wrapped_payload(text) or text or ""
    found = [ch for ch in payload.upper() if ch in letters]
    return found[0] if found else None


def parse_choices(text: str, n_options: int = 5, expect: int = 2) -> list[str] | None:
    """Parse Task 3's two-of-five selection, preserving order and dropping repeats."""
    letters = [chr(ord("A") + i) for i in range(n_options)]
    payload = _wrapped_payload(text) or text or ""
    seen: list[str] = []
    for ch in payload.upper():
        if ch in letters and ch not in seen:
            seen.append(ch)
    if not seen:
        return None
    return seen[:expect]
