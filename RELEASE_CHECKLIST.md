# Release checklist

What this repository already contains, and what has to be dropped in before the
release is complete. Everything below is a file edit — no code changes needed.

## Data

- [ ] **Replace the example records in `data/*.jsonl` with the full release.**
      Six Task 1 records, two Task 2 records and two Task 3 records are present as
      worked examples, transcribed from the paper's figures. The real files should
      hold 765 Task 1 records and 483 auxiliary items.
      Validate with `python scripts/validate_data.py` — it checks every record
      against the JSON Schemas, flags duplicate ids, and lists unscored dimensions.
- [ ] **Fill the one null score.** `4AmVjblOvy4_0_30s__brown_haired_woman__blonde_woman`
      has `I: null`: that cell is hidden behind an open menu in Figure 16. Take it
      from the original `score.json`.
- [ ] **Add video identifiers.** `figure1_left` and `figure1_right` carry real
      scores but no `youtube_id`, so the project page shows the annotation without a
      player. Adding the identifier is enough to make the video appear.
- [ ] **Complete `data/videos.csv`** with one row per released clip.

## Project page

- [ ] Run `python scripts/export_site_data.py` after any data change. The samples
      page is generated from the data files; it is never edited by hand.
- [ ] Add editorial titles and summaries for new clips in `data/clip_meta.json`.
- [ ] Link the paper: the Paper button in `docs/index.html` is disabled until there
      is an arXiv or ACL Anthology URL.
- [ ] Update the BibTeX in `docs/dataset.html` and `README.md` once the Anthology
      entry exists (page numbers, address, publisher).
- [ ] Author affiliations are not on the page. Add them under the author line in
      `docs/index.html` if they should be public.

## Repository

- [ ] Confirm the annotation license choice: CC BY-NC-SA 4.0 in `LICENSE-DATA`.
- [ ] If the clips are mirrored anywhere, document how to request access in
      `data/README.md` rather than committing video.
