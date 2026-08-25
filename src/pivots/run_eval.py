"""Run a model over PIVOTSBench and report accuracy.

Examples
--------
    # Task 1, default separate prediction, video + original transcript
    python -m pivots.run_eval --model gpt-5 --task 1

    # Ablation: no visual input, transcript with social identifiers redacted
    python -m pivots.run_eval --model qwen3-32b-vl --task 1 --no-video --redact \
        --base-url http://localhost:8000/v1

    # Score a run you already have, without calling any model
    python -m pivots.run_eval --task 1 --score-only outputs/gpt-5_task1.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import DIMENSIONS
from .data import DATA_DIR, load_task, iter_task1_items
from .frames import N_FRAMES, extract_frames, to_data_url, uniform_timestamps
from .metrics import task1_report, task2_report, task3_report
from .parse import parse_choice, parse_choices, parse_score, parse_vector
from .prompts import (
    build_messages,
    format_cue_options,
    load_template,
    redact,
    task1_joint_question,
    task1_question,
    task2_question,
    task3_question,
)


def _read_transcript(video: dict, transcript_dir: Path) -> str:
    name = video.get("transcript_file")
    if not name:
        return ""
    path = transcript_dir / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _clip_images(video: dict, video_dir: Path, n_frames: int) -> list[str]:
    name = video.get("clip_file")
    if not name:
        return []
    path = video_dir / name
    if not path.exists():
        raise FileNotFoundError(
            f"{path} is missing. Run scripts/prepare_clips.py first, or pass --no-video."
        )
    duration = float(video["end_sec"]) - float(video["start_sec"])
    frames = extract_frames(path, uniform_timestamps(duration, n_frames))
    return [to_data_url(f) for f in frames]


def run_task1(args, model) -> list[dict]:
    records = load_task(1, args.data_dir)
    results = []
    if args.setting == "joint":
        template = load_template("task1", "joint")
        for rec in records:
            transcript = _read_transcript(rec["video"], args.transcript_dir)
            images = [] if args.no_video else _clip_images(rec["video"], args.video_dir, args.n_frames)
            messages = build_messages(
                template,
                task1_joint_question(rec["subject"], rec["target"]),
                redact(transcript) if args.redact else transcript,
                image_urls=images,
            )
            raw = model.complete(messages) if model else ""
            vector = parse_vector(raw)
            for idx, dim in enumerate(DIMENSIONS):
                gold = rec["scores"][dim].get("score")
                if gold is None:
                    continue
                results.append({
                    "item_id": f"{rec['item_id']}__{dim}",
                    "dimension": dim,
                    "gold": gold,
                    "pred": vector[idx] if vector else None,
                    "raw": raw,
                })
        return results

    template = load_template("task1", args.setting)
    for item in iter_task1_items(records):
        transcript = _read_transcript(item["video"], args.transcript_dir)
        images = [] if args.no_video else _clip_images(item["video"], args.video_dir, args.n_frames)
        messages = build_messages(
            template,
            task1_question(item["subject"], item["target"], item["dimension"]),
            redact(transcript) if args.redact else transcript,
            image_urls=images,
        )
        raw = model.complete(messages) if model else ""
        results.append({
            "item_id": item["item_id"],
            "dimension": item["dimension"],
            "gold": item["gold"],
            "pred": parse_score(raw),
            "raw": raw,
        })
    return results


def run_task2(args, model) -> list[dict]:
    template = load_template("task2")
    results = []
    for rec in load_task(2, args.data_dir):
        option_frames = [] if args.no_video else [
            to_data_url(f)
            for f in extract_frames(
                args.video_dir / rec["video"]["clip_file"], rec["options_sec"]
            )
        ]
        context_frames = [] if args.no_video else _clip_images(rec["video"], args.video_dir, args.n_frames)
        messages = build_messages(
            template,
            task2_question(rec["subject"], rec["target"], rec["dimension"]),
            image_urls=option_frames + context_frames,
        )
        raw = model.complete(messages) if model else ""
        results.append({
            "item_id": rec["item_id"],
            "answer": rec["answer"],
            "pred": parse_choice(raw),
            "raw": raw,
        })
    return results


def run_task3(args, model) -> list[dict]:
    template = load_template("task3")
    results = []
    for rec in load_task(3, args.data_dir):
        frames = [] if args.no_video else [
            to_data_url(f)
            for f in extract_frames(args.video_dir / rec["video"]["clip_file"], [rec["frame_sec"]])
        ]
        messages = build_messages(
            template,
            task3_question(rec["subject"], rec["target"], rec["dimension"]),
            options=format_cue_options(rec["options"]),
            image_urls=frames,
        )
        raw = model.complete(messages) if model else ""
        results.append({
            "item_id": rec["item_id"],
            "answer": rec["answer"],
            "pred": parse_choices(raw),
            "raw": raw,
        })
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate an MLLM on PIVOTSBench.")
    parser.add_argument("--task", type=int, choices=[1, 2, 3], required=True)
    parser.add_argument("--model", help="Model name. Omit together with --score-only.")
    parser.add_argument("--base-url", help="OpenAI-compatible endpoint.")
    parser.add_argument("--setting", default="separate",
                        choices=["separate", "joint", "pairwise", "multi_stage", "in_context"],
                        help="Task 1 prediction setting or prompting strategy.")
    parser.add_argument("--no-video", action="store_true", help="Transcript-only ablation.")
    parser.add_argument("--redact", action="store_true", help="Redact explicit social identifiers.")
    parser.add_argument("--n-frames", type=int, default=N_FRAMES)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--video-dir", type=Path, default=Path("videos"))
    parser.add_argument("--transcript-dir", type=Path, default=Path("transcripts"))
    parser.add_argument("--out", type=Path, help="Where to write per-item predictions (JSONL).")
    parser.add_argument("--score-only", type=Path, help="Score an existing predictions file.")
    args = parser.parse_args()

    if args.score_only:
        results = [json.loads(line) for line in args.score_only.read_text().splitlines() if line.strip()]
    else:
        if not args.model:
            parser.error("--model is required unless --score-only is given")
        from .models import ChatModel

        model = ChatModel(args.model, base_url=args.base_url)
        runner = {1: run_task1, 2: run_task2, 3: run_task3}[args.task]
        results = runner(args, model)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            with args.out.open("w", encoding="utf-8") as fh:
                for row in results:
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    report = {1: task1_report, 2: task2_report, 3: task3_report}[args.task](results)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
