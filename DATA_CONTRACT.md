# Assignment 2 — Observed data contract

**Source inspected:** `data/Example claim table.xlsx`, workbook `Sheet1`, using `openpyxl` with calculated values. The worksheet has 220 physical/formatted rows and 26 physical columns, but only seven named columns and **10 populated data rows**. Columns H–Z and the remaining formatted rows contain no record data. No populated row has a blank value in the seven named columns; no exact duplicate populated row was observed. This is a sample, not a verified production contract.

| Exact header | Observed Excel value type | Observed interpretation / limit |
|---|---|---|
| `customer_name` | string | Customer name; precise recipient rule needs confirmation. |
| `policy_number` | string | Policy reference; not a unique claim/request ID. |
| `coverage_start_date` | datetime | Coverage start date. |
| `coverage_end_date` | datetime | Coverage end date. |
| `hospital_name` | string | Hospital name. |
| `claim_status` | string | Observed values: `REQUEST_DOC` (5), `APPROVED` (3), `REJECTED` (2). Eligibility meaning needs confirmation. |
| `document_request` | string containing JSON array | Requests on `REQUEST_DOC` rows contain document names; nonrequest rows have `[]`. Document vocabulary and wording need confirmation. |

**Proposed sample validation:** require the seven headers; ignore wholly empty formatted rows; require nonblank identifiers and parseable dates; require start ≤ end; accept only observed statuses pending business confirmation; parse `document_request` as a JSON list of nonempty strings; require a nonempty list if `REQUEST_DOC` is confirmed eligible. Reject unknown states for review. Show worksheet row and field in an error report. These rules are proposed, not confirmed Sunday policy.

**Missing contract:** a stable claim/request identifier, whether a policy can have several simultaneous requests, exact eligibility, allowed document labels, date formatting, and whether every displayed field belongs in the letter. A file hash and normalized row fingerprint can flag repeats in a POC, but cannot establish business-level idempotency.
