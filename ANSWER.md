# Assignment 2 — Additional document request letters

## 2.1 How the system works

**Fact from files.** The Excel has seven named columns: `customer_name`, `policy_number`, `coverage_start_date`, `coverage_end_date`, `hospital_name`, `claim_status`, `document_request`. It contains 10 populated customer rows: five `REQUEST_DOC`, three `APPROVED`, two `REJECTED`. `document_request` is a JSON encoded list; request rows contain one or more document names. The sample PDF shows a Thai customer letter with variable customer, policy, coverage dates, hospital and numbered document list. The worksheet has formatted empty rows; only populated rows count.

**Assumptions to confirm with claims owner.** Only `REQUEST_DOC` rows generate letters. One row represents one request for one policy; a policy may legitimately have multiple requests in separate batches. Letter wording, legal entity, contact channel, signatory, date format and dispatch method require business approval. The sample PDF is a visual example, not proof that its wording is approved. The system generates files for review and does not send them automatically.

| Step | POC behaviour | Check / evidence |
|---|---|---|
| 1. Intake | User uploads `.xlsx`; assign batch ID and file hash | Record uploader, received time, source filename |
| 2. Validate file | Require exact header names, supported types and size | Reject unreadable files and show actionable error |
| 3. Validate rows | Check nonblank identifiers, valid dates, start ≤ end, valid status, parse `document_request` as list of nonempty strings | Error report with row number; do not silently coerce unknown values |
| 4. Select | Generate only `REQUEST_DOC` rows with nonempty document list | Other statuses shown as skipped, never sent |
| 5. Render | Insert escaped data into approved versioned Thai template; create variable-length numbered list | No LLM generated customer facts or wording |
| 6. Check output | Check each expected PDF exists, opens, has pages and retains key identifiers and document items; visually inspect Thai font in sample | Batch manifest: generated / skipped / failed |
| 7. Review | Authorized user previews sample and approves batch | Record approval identity and template version |
| 8. Deliver | Provide secure download to the agreed sending team | Actual customer delivery is a separate approved workflow |

**Data contract.** Required: all seven headers. Dates must be valid date cells; `coverage_start_date` cannot exceed `coverage_end_date`. `claim_status` is one of the three observed values for this POC; future values cause an exception for owner review. On a `REQUEST_DOC` row, `document_request` must parse as a nonempty JSON list of nonempty strings. For other statuses, an empty list is valid. Policy and customer name must be present. Further rules, such as whether coverage must be active on request date, cannot be inferred from the supplied file and need a claims SME decision.

**Flow:** Excel → file and row validation → status selection → approved template + data → PDF checks → sample preview → human approval → controlled download + batch manifest.

**POC:** local batch tool, approved template, validation report and PDF previews. **Production extension:** authenticated upload, restricted storage, job queue only if batch size or duration warrants it, template lifecycle, retention policy, monitored delivery integration. Success criterion for the POC: every eligible row generates exactly one readable letter with matching fields, every ineligible row is skipped, and invalid data produces a specific error.

**POC evidence (local sample only).** The sample run reconciled 10 populated rows as 5 generated and 5 skipped, with 0 rejected and 0 generation failures. All five PDFs opened as one-page files, retained the expected customer/policy/document values, contained no unresolved placeholder, and passed a Thai visual spot check. These counts show the POC execution result, not production performance or a confirmed eligibility policy.

## 2.2 Fortnightly process with users

First hold a short discovery session with claims operations and the template owner: map the current handoffs, obtain approved wording, confirm file cutoff, exception owner, approver, dispatch channel, retention and turnaround target. Run one supervised batch alongside the current process and compare every output before switching the team to the tool. Measure time spent and error counts before claiming efficiency gains.

At each two-week cycle: (1) owner exports and checks Excel; (2) user uploads it before an agreed cutoff; (3) system shows eligible, skipped and rejected counts plus downloadable row errors; (4) user corrects the source file and reuploads; (5) approver reviews a sample plus exceptions and confirms; (6) system generates or releases PDFs; (7) owner performs delivery via the agreed channel; (8) manifest and audit record are retained according to policy. Reminders support the cycle, but a calendar trigger alone must not approve or send letters.

For duplicate prevention, store a stable request key agreed with the business, ideally claim/request ID from the source system. **The sample Excel has no claim ID**, so `policy_number` alone is unsafe: multiple claims or document requests may share it. A POC can flag an identical normalized row plus file hash and template version for review, but cannot guarantee business-level deduplication. Require an upstream unique request ID for reliable production idempotency. A rerun records whether it reuses, replaces or versions a previous letter; it must not silently create another customer delivery.

Own the process explicitly: claims operator fixes data, document owner approves template wording, batch approver releases letters, engineering supports failures. Agree response times and an exception path with these owners. Review the first three cycles together, then use an issue log and periodic changes review.

## 2.3 Failure, prevention and recovery

| Failure | Detect / prevent | Recover / notify |
|---|---|---|
| Damaged or wrong Excel; renamed header | Parse and schema check before work | Reject batch with exact missing/extra headers; user reexports |
| Blank, invalid or duplicate rows | Row validation; explicit duplicate review | Quarantine affected rows; process unaffected rows only if owner approves partial batches |
| Unknown status or document type | Controlled status values; document list validation | Stop affected row; claims owner resolves wording or mapping |
| Wrong business meaning | SME signoff of eligibility and template | Halt release, correct rules, regenerate with new version; assess already sent letters |
| Missing placeholder, Thai glyph or broken PDF | Template publish check, embedded Thai font, PDF open/text and visual sample checks | Block release; fix template/font, rerun failed rows |
| Process crash or storage exhaustion | Atomic output writes, manifest and health checks | Resume incomplete batch without redelivery; alert operator |
| Accidental repeat upload or send | File hash plus request ID when available; delivery state | Show prior run and require explicit override with reason |
| Unauthorised access or PII exposure | Role restrictions, encryption, minimal logs, private storage | Revoke access, investigate using audit trail, follow company incident process |

Failures are visible at batch and row level. A `try/except` without error reports, review state and recovery steps would not make this safe for customer communications.
