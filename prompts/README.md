# Prompts

Transcribed from Appendix F of the paper (Figures 7–13). Placeholders are filled by
`src/pivots/prompts.py`:

| Placeholder     | Filled with                                                        |
|-----------------|--------------------------------------------------------------------|
| `{definition}`  | `prompts/pivots_definition.md`                                      |
| `{transcript}`  | The clip transcript, original or redacted                           |
| `{question}`    | The directional question, e.g. "the S score from the Man in the white jacket to the Man in the black robe" |
| `{options}`     | Task 3 answer options                                               |

Visual input is passed as `image_url` content blocks alongside the text block: eight
frames uniformly sampled from the clip (the paper's default; 12- and 15-frame sampling
score 1.2 and 2.4 points higher, Appendix H.3). Task 2 prepends the five option frames
before the eight context frames.

Every template ends with the same contract: the answer is wrapped in `###...###`.
`src/pivots/parse.py` is the matching parser.

| File                    | Used for                                            |
|-------------------------|-----------------------------------------------------|
| `task1_separate.txt`    | One dimension, one direction — the default setting  |
| `task1_joint.txt`       | All six dimensions, one direction                   |
| `task1_pairwise.txt`    | All six dimensions, both directions                 |
| `task2_keyframe.txt`    | Key-frame identification                            |
| `task3_causal.txt`      | Visual cue causal analysis                          |
| `multi_stage.txt`       | Heuristic injection, four-phase protocol            |
| `in_context.txt`        | Heuristic injection, cue checklist + worked example |
