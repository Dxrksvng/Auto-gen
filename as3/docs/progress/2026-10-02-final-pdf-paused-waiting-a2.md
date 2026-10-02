# 2026-10-02 — Final PDF (A2-4) paused, waiting for A2 to finish

**What changed:** added a PDF build pipeline and A3 helper artifacts. No edit to `as2/`, and no edit to the existing `as3/ANSWER.md`. `as3/USER_GUIDE.md` was briefly overwritten and then restored from `archive/USER_GUIDE_2026-10-01_en.md` (the file name says "en" but its content is Thai). My own guide version is kept at `archive/USER_GUIDE_session-b_th.md`.
**Why paused:** `as2/` is still being fixed (git log shows commits from 11:46 on; `renderer.py` is modified, `letter.py` and `verify.py` are untracked, `docs/A2_CHANGELOG.md` does not exist). The existing `as3/ANSWER.md` (Thai, written 06:43) says A2 is unfixed, so its A2 claims will be wrong once A2 is done.

## Found on disk
- A complete earlier A3 rewrite already exists: `ANSWER.md`, `USER_GUIDE.md/.pdf`, `docs/A2_A3_CONSISTENCY.md`, `scripts/check_a2_a3.py`, `docs/diagrams/*.png`, `docs/guide-images/`, `examples/`, `mockup/s*.html`.
- Files added in this session sit in separate folders and duplicate part of that work: `tools/`, `samples/`, `definitions/`, `templates/`, `render-test/`, `diagrams/`, `assets/`, `mockup/screens/`, `USER_GUIDE.src.md`.

## Build pipeline state (`tools/build_submission.py`)
Output goes to `final/submission/Assignment_2_to_4.pdf` (a dry-run file is there now, 30 pages, built from the old A3; do not submit it). Fonts: Sarabun (OFL) and DejaVu, in `assets/fonts/`.
Done: title page, table of contents, [TO CONFIRM] list on the last page, Mermaid to PNG, relative links removed, tables kept with their intro line.
Still to do:
1. Mermaid ER diagram text is clipped; wait for fonts to load before rendering.
2. Wide diagrams (A4 diagram 1 and the ER diagram) are too small at A4 portrait; put them on landscape pages.
3. Check the A3 PNG diagrams (`docs/diagrams/`) are legible at 100% zoom.
4. Automated checks and `final/submission/CHECKLIST.md`: no duplicated honorific, no TODO, no forbidden words in 3.4, no absolute paths, no keys, size under 15 MB, page count.

## What's next
After A2 is finished (changelog exists, tests pass):
1. Update `as3/ANSWER.md` tables to the fixed A2 and rerun `scripts/check_a2_a3.py`.
2. Decide which A3 set is canonical (earlier set vs. the extra files from this session).
3. Rebuild the PDF, inspect every page, write `CHECKLIST.md`.
