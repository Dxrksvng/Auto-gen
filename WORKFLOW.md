# Assignment 2 — Workflow (2.1)

```text
Business file → intake (batch ID, hash, time)
  → file/schema validation (stop batch on failure)
  → row validation (ready / warning / rejected)
  → normalized claim/request record
  → confirmed eligibility and document rules
  → immutable LetterData + approved template version
  → PDF rendering → PDF open/content/placeholder checks
  → preview and agreed human approval → release boundary
  ↘ row errors, batch manifest, audit references
```

For the observed sample, `REQUEST_DOC` looks like the candidate status for generation; this must be confirmed with the claims owner. `APPROVED` and `REJECTED` should be accounted for as skipped if that interpretation is confirmed. Do not pass spreadsheet rows directly into the renderer or let an LLM invent wording. The provided `data/template_test.pdf` is a Thai visual sample with placeholders and a numbered request list, not evidence of approved wording.

Proposed record states: `RECEIVED`, `READY`, `GENERATED`, `REVIEW_REQUIRED`, `READY_FOR_RELEASE`, `RELEASED`, plus `REJECTED_INPUT`, `GENERATION_FAILED`, and `RELEASE_FAILED`. Preserve batch ID, source row, source hash, template version and output reference. Reconcile populated rows as generated + skipped + rejected + failed. Sending is a separately agreed integration.
