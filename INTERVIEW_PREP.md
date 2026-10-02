# Assignment 2 — Interview preparation

1. **Why not use an LLM?** The input and output are structured and customer-facing. Deterministic validation and an approved template are more reproducible and auditable. AI may assist onboarding, with human approval before configuration is published.
2. **Why validate before generating?** A clear rejection is safer and cheaper to correct than a plausible but incorrect customer letter.
3. **Why not use `policy_number` for deduplication?** A policy can have more than one claim or request. Production needs a stable request/claim ID plus template/request version semantics.
4. **What happens when one row is bad?** Isolate it, report row/field/action, and continue valid rows only if the business accepts partial batches. Schema-wide failures stop the batch.
5. **How do you rerun safely?** Retain batch/source identity and row state, retry transient failures within bounds, and rerun failed rows without redelivering successful ones.
6. **How do you prevent customer A's data entering customer B's letter?** Build an immutable object per row, render in isolation, retain source-output references, reconcile counts, test mappings and review before release.
7. **Why separate generation and delivery?** A valid PDF can still fail to reach the customer; retries and evidence differ. Separate states prevent regeneration or duplicate sending.
8. **What would you automate first?** Validation, deterministic rendering, error reporting and reconciliation. Begin with user-triggered supervised batches, then increase scheduling after rules stabilize.
9. **What changes for production?** Add authenticated intake, role controls, private durable storage, template publishing/versioning, durable job state, monitoring, audit events, retention and agreed delivery integration.
10. **What did the POC prove?** It read the supplied workbook, reconciled all 10 populated rows, created five verified one-page PDFs, reported skipped rows and safely reused batch identity on rerun. It did not prove business-rule correctness, approved wording, scale, SLA or compliance.
