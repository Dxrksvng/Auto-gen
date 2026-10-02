# Assignment 2 — Completion report

## Evidence inspected

- Official confidential brief: delivery instruction on page 2 and Assignment 2 on page 7.
- `data/Example claim table.xlsx`: `Sheet1`, seven named columns, 10 populated rows, status split 5/3/2.
- `data/template_test.pdf`: one-page Thai layout with recipient, policy, coverage dates, hospital and numbered document placeholders.
- Existing combined `../Assignment_2_to_4.pdf`: eight pages; Assignment 2 occupies pages 2–3 and text is extractable.

## Final design

2.1 uses intake identity, fail-before-generate validation, normalization, confirmed business rules, immutable LetterData, approved template, PDF checks, review/release separation and reconciliation. 2.2 uses an assisted two-week runbook with correction, confirmation, row-level rerun and change/version control. 2.3 distinguishes file, data, business, template, mapping, duplicate, infrastructure, deployment and delivery failures with detection, prevention and recovery.

The runtime is deterministic. AI could later suggest header mappings or onboarding configuration, but a human must review and publish deterministic configuration before runtime use.

## POC result

The local CLI generated `poc/output/batch_69493eedf44c`. Manifest result: 10 populated, 5 candidate eligible, 5 skipped, 0 rejected, 5 generated, 0 failed. The PDFs passed parse/content/placeholder checks and a Thai visual inspection. Filenames contain worksheet row and a policy hash rather than customer data. Same source content resolves to the same batch and filenames.

## Unresolved business decisions

- Confirm that `REQUEST_DOC` is the complete eligibility rule.
- Supply a stable claim/request ID for production idempotency.
- Approve final wording, legal entity, contact details, date format and template/font.
- Assign correction, approval, release and delivery ownership.
- Define warning versus rejection, partial batch policy, delivery channel and retention.

## Main risks

The largest risk is wrong customer/data mapping. Stop release when suspected and trace the affected source rows and outputs. The sample lacks a request ID, so the POC detects identical technical reruns but cannot distinguish every legitimate new request from a business duplicate. Generated does not mean delivered.

## Files to study before interview

1. `ANSWER.md`
2. `DATA_CONTRACT.md`
3. `OPERATIONS.md`
4. `FAILURE_MODES.md`
5. `ARCHITECTURE.md`
6. `ASSUMPTIONS.md`
7. `poc/README.md`
8. `poc/output/batch_69493eedf44c/manifest.json`
