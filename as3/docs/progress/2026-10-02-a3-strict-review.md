# 2026-10-02 — Strict review of Assignment 3 answer (3.1-3.4)

**What changed:** nothing in code or answer text. Review only, of `assignment-brief/Assignment_2_to_4.pdf` pp.4-5 and `as3/ANSWER.md`.
**Why:** pre-interview check. Not read this pass: `TRADEOFFS.md`, `GOVERNANCE.md`, `DOCUMENT_DEFINITION.md`. No user-test evidence found in the PDF or ANSWER.md.

## Scores
3.1 = 6.5/10, 3.2 = 5/10, 3.3 = 5/10, 3.4 = 3.5/10. Verdict: not ready to submit (about one day of fixes).

## Findings
- 3.1 claims A2 "audit core" is reused; A2 POC has none. A2 hard-codes headers (`validation.py:19`), letter text (`renderer.py:36-52`), macOS font path (`renderer.py:15-17`). No unsupported-scope list.
- 3.2 has no template-authoring path (Word/Google Docs + fields), no rendering-engine choice, no legal/compliance approval gate, no upload retention, no ownership/support, thin pilot plan, ASCII diagram only.
- 3.3 risks are generic; no alternatives considered (SaaS, Mail Merge, Apps Script, per-team scripts).
- 3.4 has no screenshots, no error table (A2 shows codes like `UNKNOWN_STATUS`), no contact, no FAQ, English only. Re-upload step conflicts with A2 2.2 duplicate prevention.

## What's next
1. Add template-authoring path and Thai-layout test plan to 3.2.
2. Fix "audit core" wording; add reuse / rebuild / not-built table to 3.1.
3. Rewrite 3.4 with mockups, error table, checklist, contact, Thai labels; plan a 3-5 user test (as a plan, not a result).
4. Add legal gate, retention, RACI, alternatives, phased pilot, one concrete Document Definition.
