# Assignment 2 — Two-week operating process (2.2)

1. Agree with business owner what a row means, eligibility, approved wording, cutoff, exception owner, approval and delivery responsibilities.
2. Operator exports the agreed workbook and submits it. System records batch identity, file hash, period and template version.
3. Preflight stops malformed files; row checks return ready, skipped, warning and rejected counts with a downloadable row/field/action report.
4. Operator corrects and resubmits errors. A corrected file becomes a linked processing version, not an invisible overwrite.
5. Authorized user reviews counts, sample PDFs and exceptions, then confirms generation/release under the agreed policy.
6. System generates, validates and reconciles every populated row. Retry transient failures within bounds; rerun failed rows only after correction.
7. Sending team uses the agreed channel; record delivery status separately. Close the batch with manifest and issue log.

Start with an assisted run every two weeks and compare outputs with the existing process. Add reminders or scheduling after rules stabilize; advance to greater automation only with measured reliability and agreed controls. Business owns rules and wording; operator owns input corrections; engineering owns defects and deployment. These are proposed responsibilities, not identified Sunday roles.

The sample lacks a claim/request ID. `policy_number` alone cannot safely prevent duplicate business requests. Flag exact file/row repeats now; require a source request ID and agreed version semantics for reliable production deduplication. Distinguish accidental rerun, corrected source and genuinely new request.
