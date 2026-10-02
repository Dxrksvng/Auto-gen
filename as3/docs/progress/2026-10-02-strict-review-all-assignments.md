# 2026-10-02 — Strict review of A1 / A2 / A3-4 submission

**What changed:** nothing in code. Read-only review; probe scripts lived in the session scratchpad (not saved).
**Why:** pre-submission interview-risk check against `assignment-brief/Forward Deployed AI-Eng Assignment 2026.pdf`.
**Not verified:** A1 LLM path (no API key), A4 POC (Node, not run), Thai rendering outside macOS `sips`, `Assignment_2_to_4.pdf` page images beyond p4/p7.

## Run results (actually executed)
- A1 `pytest`: 12 passed (tests use the 10-game sample only). A2 `pytest`: 6 passed (py3.13 framework install; needs PyMuPDF + reportlab, no requirements file).
- A1 offline parser drops time/player limits for "an hour", "30 minutes or less", "two hours max", "less than 2 hours", "ไม่เกินชั่วโมง", "เกมสำหรับ 5 คน", "for four players". On the 10-game fallback this returns Wingspan (70 min) for "ไม่เกินชั่วโมง" and a 2-4 player game for 5 players.
- A1 `sqlite` snapshot is gitignored; a reviewer cloning gets the 10-game fallback, so outputs differ from the local 4,621-game run.
- A2 PDFs: "เรียน คุณ คุณสมชาย ..." duplicated honorific in all 5; English "Medical Report" in 2 Thai letters; CE dd/mm/YYYY; letter text is not the supplied template (no company, app, contact, closing, logo).
- A2 renderer does not escape markup: hospital "รพ. <foo>" rendered as "รพ." and counted as generated; `verify_pdf` checks only policy, name, documents.
- Answer says "Insert escaped data" and "reuse the validated ... audit core from A2": neither exists in the POC.
- `as4/ANSWER.md` (4 methods) contradicts `Assignment_2_to_4.pdf` (tarot only, "do not launch multiple methodologies").

## What's next (fix order)
1. A2 renderer: strip leading "คุณ" once, `xml.sax.saxutils.escape` all fields, verify hospital + dates, add regression tests.
2. A1 parser: add "an hour"/"or less"/"less than"/"max"/Thai no-number "ชั่วโมง", word numbers, "for N"/"สำหรับ N คน"; add tests on both datasets; decide strict vs inclusive "under".
3. Align PDF and as4 repo; fix claims in 2.1 and 3.1; add a concrete Document Definition example and template-authoring path to 3.2.
4. Make A4 diagrams real drawings; add named competitors or drop the market claim.
5. Ship dataset or document that the sqlite is absent; add requirements.txt for as2.
