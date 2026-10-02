# Assignment 2 — Answer for combined PDF

The input example has seven columns and 10 populated rows. Five rows have `REQUEST_DOC`; whether this is the complete eligibility rule needs confirmation. The Thai sample PDF is a layout reference, not approved wording. The core should be deterministic: validate data, apply confirmed rules, fill an approved versioned template, then inspect the PDF. An LLM is unnecessary for this structured runtime flow.

## 2.1 How does the system work?

```text
Excel intake → preflight/schema/row checks → normalized record
→ eligibility and document rules → approved template → PDF
→ output checks → preview/release → batch manifest
```

Record file hash, batch ID, worksheet row and template version. Reject unreadable or structurally wrong workbooks before generation. Validate each populated row; give a row/field/action error report. Parse `document_request` as a list, preserve the variable length numbered list, and render one letter per eligible request after the claims owner confirms status semantics. Check each PDF opens, contains expected reference/request text and has no unresolved placeholders; visually inspect Thai text when changing templates/fonts. Keep generated and delivered states separate. Reconcile every source row as generated, skipped, rejected or failed. The POC can be local; authenticated access, durable job state and storage are proposed production additions.

The local POC run produced five one-page PDFs from the five candidate rows and skipped the other five populated rows; no row was rejected and no generation failed. Automated checks also exercise an invalid-row rejection and deterministic rerun identity. These are execution facts for the supplied sample, not production metrics.

## 2.2 How would I run it every two weeks with the user?

First agree on the source export, approved wording, eligibility, cutoff, exception owner, approver and sending channel. Run the first cycles with the user and compare documents with the current process. Each cycle: prepare and submit file; validate and show counts/errors; correct and resubmit; preview exceptions and sample output; confirm generation/release; reconcile and close the batch. Reminders can support the cadence, but a calendar trigger does not replace business confirmation. Maintain an issue log and version rule/template changes.

For safe reruns, link attempts to a batch and source hash and rerun failed rows only. The sample has no claim/request ID, so policy number alone is not a safe idempotency key. Require a stable upstream request identifier for production; until then, flag exact repeats for human review and prevent silent duplicate delivery.

## 2.3 Can it fail? How do I prevent or resolve it?

Yes. File/schema errors stop the batch and return actionable feedback. Invalid rows are isolated; unknown business cases go to the owner rather than guessed. Template and Thai font issues are caught by publish tests and PDF checks, then fixed or rolled back before release. Rendering/storage interruptions use bounded retry and row-level resume. Duplicate uploads and sends are checked against prior runs and delivery state. Wrong customer-data mapping is high severity: stop release, isolate outputs, trace source-to-PDF references and regenerate after correction. A generated PDF is not proof of successful customer delivery, so delivery needs its own status and recovery path. See `FAILURE_MODES.md` for the full matrix.
