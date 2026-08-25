"""Building the OpenAI-style multimodal messages used in the paper."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from . import CUES, DIMENSION_NAMES
from .data import PROMPT_DIR

TEMPLATES = {
    ("task1", "separate"): "task1_separate.txt",
    ("task1", "joint"): "task1_joint.txt",
    ("task1", "pairwise"): "task1_pairwise.txt",
    ("task1", "multi_stage"): "multi_stage.txt",
    ("task1", "in_context"): "in_context.txt",
    ("task2", "default"): "task2_keyframe.txt",
    ("task3", "default"): "task3_causal.txt",
}

# Kinship terms, titles and honorifics replaced in the redacted-transcript ablation.
ROLE_TERMS = (
    r"father|mother|dad|mom|mum|papa|mama|son|daughter|brother|sister|grandpa|grandma|"
    r"grandfather|grandmother|husband|wife|uncle|aunt|cousin|nephew|niece"
)
TITLE_TERMS = r"your honor|boss|sir|ma'am|madam|doctor|dr\.|professor|officer|captain|coach|chef"


@lru_cache(maxsize=None)
def load_template(task: str, setting: str = "default") -> str:
    key = (task, setting)
    if key not in TEMPLATES:
        raise KeyError(f"no template for {key}; available: {sorted(TEMPLATES)}")
    return (PROMPT_DIR / TEMPLATES[key]).read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def load_definition() -> str:
    return (PROMPT_DIR / "pivots_definition.md").read_text(encoding="utf-8")


def redact(transcript: str) -> str:
    """Replace explicit social identifiers while preserving syntax and tone."""
    out = re.sub(TITLE_TERMS, "[TITLE]", transcript, flags=re.I)
    out = re.sub(ROLE_TERMS, "[PERSON]", out, flags=re.I)
    return out


def task1_question(subject: str, target: str, dimension: str) -> str:
    name = DIMENSION_NAMES[dimension]
    return (
        f"Provide the unidirectional {dimension} ({name}) score from {subject} to {target}."
    )


def task1_joint_question(subject: str, target: str) -> str:
    return f"Provide the unidirectional PIVOTS scores from {subject} to {target}."


def task1_pairwise_question(subject: str, target: str) -> str:
    return (
        f"Sequentially provide the unidirectional PIVOTS scores from {subject} to "
        f"{target}, and from {target} to {subject}."
    )


def task2_question(subject: str, target: str, dimension: str) -> str:
    return (
        f"Which frame best reflects the {dimension} ({DIMENSION_NAMES[dimension]}) "
        f"dimension score from {subject} to {target}?"
    )


def task3_question(subject: str, target: str, dimension: str) -> str:
    return (
        f"Which two elements in this image best reflect the {dimension} "
        f"({DIMENSION_NAMES[dimension]}) dimension score from {subject} to {target}?"
    )


def format_cue_options(cue_keys: list[str]) -> str:
    letters = "ABCDE"
    return "; ".join(f"{letters[i]}: {CUES[key]}" for i, key in enumerate(cue_keys))


def build_messages(
    template: str,
    question: str,
    transcript: str = "",
    options: str = "",
    image_urls: list[str] | None = None,
) -> list[dict]:
    text = (
        template.replace("{definition}", load_definition())
        .replace("{transcript}", transcript)
        .replace("{question}", question)
        .replace("{options}", options)
    )
    content: list[dict] = [{"type": "text", "text": text}]
    for url in image_urls or []:
        content.append({"type": "image_url", "image_url": {"url": url}})
    return [{"role": "user", "content": content}]
