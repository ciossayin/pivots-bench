# PIVOTSBench

**Evaluating fine-grained interpersonal relationship reasoning in multimodal large language models**
Shuxiang Zhang¹\* · Yiting Yin²\* · Wenxuan Song³ · Yuhang Wu³† · Miao Liu³‡ — EMNLP 2026, Main Conference
¹Sun Yat-sen University · ²University of Michigan · ³Tsinghua University · \*Equal contribution · †Project lead · ‡Corresponding author

Project page: **https://ciossayin.github.io/pivots-bench/** · [Paper](https://arxiv.org/abs/2606.23092) · [Poster](https://ciossayin.github.io/pivots-bench/assets/poster.pdf)

People do not read a relationship as a category. They read it as a set of graded,
*directional* judgments, from faces and posture as much as from words. PIVOTS asks
whether multimodal LLMs can do the same: score a relationship on six
psychology-grounded dimensions, separately for each participant's point of view,
from a 30-second clip and its transcript — then point at the frame and the visual
cue that carry the judgment.

Two clips can both be labelled *parent–child* and sit at opposite ends of nearly
every dimension. Category labels cannot express that; dimensions can.

## The six dimensions

Each is a five-point bipolar scale from −2 to +2, scored once per direction.

| | Dimension | Axis |
|---|---|---|
| **P** | Power | Egalitarian ↔ hierarchical |
| **I** | Involvement | Superficial ↔ intense |
| **V** | Valence | Positive ↔ negative |
| **O** | Objective | Socioemotional ↔ task-oriented |
| **T** | Permanence | Temporary ↔ enduring |
| **S** | Stance | Cooperative ↔ competitive |

Full rubrics, with behavioral and psychological observables for all thirty anchors,
are in [`prompts/pivots_definition.md`](prompts/pivots_definition.md).

## The three tasks

1. **Six-dimensional scoring** — predict the six scores for A→B. Five options, chance 20%.
2. **Key-frame identification** — pick the frame that best shows a given dimension. Chance 20%.
3. **Visual cue causal analysis** — pick the two cues in that frame that support the score.
   Half credit for one, so chance is 40%.

## Headline results

Task 1 average accuracy (%), Social-IQ 2.0 subset. Full tables and ablations on the
[results page](https://ciossayin.github.io/pivots-bench/leaderboard.html).

| Model | Avg | Task 2 | Task 3 |
|---|---|---|---|
| GPT-5 | 56.91 | 62.15 | 60.25 |
| Gemini-2.5-pro | 47.71 | 46.63 | 48.00 |
| Qwen3-32B-VL | 34.54 | 35.29 | 33.50 |
| Qwen3-8B-VL | 27.90 | 34.75 | 31.00 |
| Qwen3-4B-VL | 24.33 | 28.59 | 30.17 |

Human annotators agree with each other exactly 83.87% of the time.

## Repository layout

```
data/         annotations (JSONL), JSON Schemas, statistics, clip metadata
prompts/      every prompt from the paper, plus the PIVOTS rubric
src/pivots/   evaluation toolkit: prompt building, frame sampling, parsing, metrics
scripts/      data validation, agreement, site export
results/      the paper's tables, machine-readable
docs/         the project page (GitHub Pages)
```

## Quick start

```bash
git clone https://github.com/ciossayin/pivots-bench.git
cd pivotsbench
pip install -r requirements.txt

python scripts/validate_data.py                      # check the release files
python -m pivots.run_eval --task 1 --model gpt-5     # any OpenAI-compatible endpoint
```

Run against a local server instead:

```bash
python -m pivots.run_eval --task 1 --model qwen3-32b-vl --base-url http://localhost:8000/v1
```

Reproduce an ablation row:

```bash
python -m pivots.run_eval --task 1 --no-video --redact --model qwen3-32b-vl   # redacted, text only
python -m pivots.run_eval --task 1 --setting joint --model qwen3-32b-vl       # all six at once
python -m pivots.run_eval --task 1 --setting multi_stage --model qwen3-32b-vl # heuristic prompt
```

Set `PIVOTS_API_KEY` and, if needed, `PIVOTS_BASE_URL`. Eight frames are sampled
uniformly per clip by default (`--n-frames`); the paper's Appendix H.3 reports 12
and 15 frames as slightly stronger.

## Getting the videos

The repository releases annotations, not video.

- **Social-IQ 2.0 clips** come from the [Social-IQ 2.0 Challenge](https://github.com/abwilf/Social-IQ-2.0-Challenge)
  under its own license.
- **YouTube material** is referenced by identifier and time span only.

Place the 30-second clips in `videos/` under the `clip_file` names in
`data/task1_scoring.jsonl`, and transcripts in `transcripts/`.

## Licensing

Code is MIT. Annotations are CC BY-NC-SA 4.0, for academic research. The underlying
videos remain under their original terms. See [`LICENSE-DATA`](LICENSE-DATA) and the
intended-use statement in [`data/README.md`](data/README.md).

PIVOTS is an analysis instrument, not a deployable system. Do not use it to score
real people without their knowledge, or in high-stakes or persuasive settings
without human oversight.

## Citation

```bibtex
@inproceedings{pivotsbench2026,
  title     = {PIVOTS-Bench: Evaluating Fine-Grained Interpersonal Relationship
               Reasoning in Multimodal Large Language Models},
  author    = {Zhang, Shuxiang and Yin, Yiting and Song, Wenxuan and
               Wu, Yuhang and Liu, Miao},
  booktitle = {Proceedings of the 2026 Conference on Empirical Methods in
               Natural Language Processing},
  year      = {2026},
  eprint        = {2606.23092},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CL}
}
```
