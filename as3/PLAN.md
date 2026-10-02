# Assignment 3 — Completion plan

## Done (2026-10-02, rewrite on top of the A2 code as it is, not a "fixed" A2)

- [x] Read A2 code, `../as2/ANSWER.md` and the previous A3 files; found that A2 is not fixed (no `docs/A2_CHANGELOG.md`, `poc/*.py` unchanged since 2026-10-01).
- [x] Rewrote `ANSWER.md` (Thai): 3.1 reuse/rebuild/missing table with file:line, phase-1 supported vs not; 3.2 design; 3.3 trade-offs and alternatives; 3.4 pointer to the guide.
- [x] Real Thai rendering test (HTML -> PDF, two engines, two fonts) and DOCX field test: `docs/rendering-test/`.
- [x] Two diagrams (Mermaid -> PNG): `docs/diagrams/`.
- [x] Document Definition examples (request letter, renewal sketch): `examples/definitions/`.
- [x] User guide (Thai) `USER_GUIDE.md` + `USER_GUIDE.pdf`; mockup + screenshots; 3 sample Excel files; message catalog.
- [x] Checks: `scripts/check_guide_words.py`, `scripts/check_a2_a3.py` -> `docs/A2_A3_CONSISTENCY.md`.
- [x] Usability test plan (no results): `docs/usability-test-plan.md`.

## Not done / blocked

- [ ] DOCX -> PDF (LibreOffice) Thai rendering test: LibreOffice not installed; needs approval to install.
- [ ] Thai rendering test on Linux (the likely production OS) [TO CONFIRM].
- [ ] Run the usability test with 3-5 real people (plan only).
- [ ] Fix A2 (list in `ANSWER.md` 3.1 tables b and c); then re-run `scripts/check_a2_a3.py` and update the statements that flip.
- [ ] Rebuild the combined `Assignment_2_to_4.pdf` from the final A2, A3, A4 (A3 here is now much longer than the A3 section of the current combined PDF; decide how much goes into the PDF and how much stays as linked files).
- [ ] Stakeholder answers to the [TO CONFIRM] list at the end of `ANSWER.md`.
