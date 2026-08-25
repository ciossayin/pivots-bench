# Dataset card

## Summary

PIVOTSBench annotates 191 thirty-second video clips of multi-party interaction with
**directional** interpersonal relationship scores on six dimensions, plus the visual
evidence behind each score. It is built to test whether multimodal LLMs can reason
about fine-grained social dynamics rather than assign coarse relationship categories.

| | |
|---|---|
| Clips | 191 — 121 from Social-IQ 2.0, 70 from YouTube |
| Clip length | 30 seconds |
| Directional pairs per dimension | 765 (595 Social-IQ 2.0, 170 YouTube) |
| Task 1 items | 4,590 = 765 × 6 dimensions |
| Auxiliary items (Tasks 2 and 3) | 483 |
| Label space | −2, −1, 0, +1, +2 |
| Agreement | Krippendorff's α 0.8125 (ordinal); 83.87% exact |
| Language | English |

## Files

| File | Contents |
|---|---|
| `task1_scoring.jsonl` | One record per directional pair, six dimension entries each: score, evidence timestamp, cue tags, rationale |
| `task2_keyframe.jsonl` | Key-frame identification items: five candidate timestamps and the answer |
| `task3_causal.jsonl` | Visual cue items: five cue options and the two correct ones |
| `videos.csv` | Clip inventory: source, identifier, time span, character count, tone |
| `clip_meta.json` | Editorial titles, summaries and dialogue excerpts for the project page — presentation only, no annotations |
| `schema/` | JSON Schema per task, plus the dimension and cue vocabularies |
| `stats/` | Label distribution, per-dimension agreement, headline benchmark statistics |

Validate everything with `python scripts/validate_data.py`.

## Sources and selection

**Social-IQ 2.0** (121 clips). A subset focused on explicit social interaction —
debate and informal conversation. News interviews and clips carrying text overlays
were removed to limit visual leakage, and everything was segmented uniformly into
30-second clips.

**YouTube** (70 clips). Collected to counter the bias toward overt, expressive
behavior. Targeted on interaction dynamics (persuasion, conflict resolution) and on
relational context: intimate and dissolved partnerships, sibling ties, and
zero-acquaintance pairs with divergent ideological backgrounds. Relationship signal
in this subset lives in the overall atmosphere rather than in localized gestures,
which makes it less suited to key-frame and cue-level annotation — an accepted
trade-off for coverage.

Every clip had to satisfy: multiple speakers visible and audible; interaction longer
than 30 seconds; social dynamics not readable off a trivial symbol.

The two halves differ by design. Social-IQ 2.0 skews positive (61.6%) and
documentary; the YouTube half skews serious (59.4%) and interview-driven.

## Annotation

Model-first, human-calibrated. The six-dimension rubric, reference evidence and clip
metadata were consolidated into one prompt; GPT-5 produced initial per-character
scores; annotators then verified every score against the definitions and revised
25.3% of them. Extreme scores (±2) received explicit scrutiny, and each dimension was
judged independently of the others — a couple in a heated argument is faithfully
annotated I = +2 with V = −2.

Alongside each verified score, annotators recorded the timestamp of the frame that
best supports it and tagged the cues visible there, drawn from a fixed vocabulary:
facial expression, body posture, proximity, body height, hand gesture, social norms,
gaze, context, attire, contact.

At most three characters per clip were kept, chosen by dominance and role in the
relationship. Where the source identifiers were weak, characters were relabeled
descriptively ("woman in yellow", "man on the right").

**Bias check.** On 35 clips, fully manual annotation was compared against
model-assisted annotation: Cohen's κ = 0.977, so the model-first workflow introduced
no observable bias.

**Agreement.** Ordinal Krippendorff's α over an annotator × item matrix: 0.8125
overall, 83.87% exact. Power scores lowest on α (0.6434) at the *highest* exact
agreement (86.23%), because over 70% of its labels are 0 and severe class imbalance
deflates the coefficient. Tasks 2 and 3 additionally dropped items with ambiguous or
one-sided cue selections.

Annotation was carried out by the paper's authors. No crowdworkers were recruited or
paid.

## Intended use

Research on multimodal social reasoning: benchmarking, error analysis, and
evaluation-driven development of models that reason about interpersonal dynamics.

## Out of scope

- Scoring real individuals without their knowledge or consent.
- Any deployed system that acts on a relationship score — hiring, moderation,
  matchmaking, therapeutic or clinical judgment — without human oversight.
- Inference of emotional state or relationship quality presented to a user as fact.

The construct is a research operationalization, not a measurement of ground truth
about the people on screen.

## Limitations

- **English only.** No claim transfers to other languages or cultural settings.
- **Annotator homogeneity.** All annotators share a cultural and linguistic
  background and are not native English speakers. Valence and objective are the
  dimensions most exposed to this.
- **Label imbalance.** Power is 71% zeros; stance and valence lean positive. Report
  per-dimension results, and treat a single average with care.
- **Scale.** 765 directional pairs is small enough that per-dimension differences of
  a few points on the YouTube subset are within run-to-run noise.
- **Source skew.** Both halves are public, performed-for-camera material. Private,
  unperformed interaction is not represented.

## Licensing

Annotations: CC BY-NC-SA 4.0 (see `../LICENSE-DATA`). Code: MIT.

No video, audio or extracted frames are redistributed. Social-IQ 2.0 clips must be
obtained from the original challenge under its license; YouTube material is
referenced by identifier and time span, and retrieving it is the user's
responsibility under YouTube's Terms of Service.
