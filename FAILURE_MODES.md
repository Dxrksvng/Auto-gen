# Assignment 2 — Failure analysis (2.3)

| Failure / impact | Detect and prevent | Recover |
|---|---|---|
| Wrong, corrupt or empty workbook; no safe output | File and header preflight, published input template | Stop batch; give exact error; resubmit. |
| Invalid row or unknown status/document value; wrong content | Row checks and controlled rules | Isolate row; business corrects or clarifies; rerun that row. |
| Wrong customer/data mapping; privacy and communication harm | Immutable per-row LetterData, source/output reference, reconciliation, tests | Stop release, isolate affected outputs, investigate scope, correct and regenerate under incident process. |
| Broken template, placeholder or Thai glyph; unreadable letter | Versioned template, publish tests, PDF parse/text and visual checks | Block release, roll back or repair template/font, rerender affected rows. |
| Duplicate upload or accidental resend | File hash, row fingerprint, future request ID, separate delivery state | Show previous run; require explicit controlled regeneration; suppress duplicate delivery. |
| Partial render/storage failure; missing PDFs | Per-row states, atomic persistence, batch reconciliation | Bounded retry if transient; rerun failures only. |
| Wrong period/file or approval mistake | Period and template displayed at review, sample preview, role controls | Cancel before release where possible; correct and version the batch. |
| Deployment regression | Sample/golden document tests, staged rollout | Stop affected release and roll back. |
| Delivery failure after valid generation | Separate generated/delivered states | Retry delivery under agreed integration rules without regenerating or redelivering successful rows. |

Do not retry malformed data or unresolved business meaning. Error reports should be usable by operations staff without reading stack traces.
