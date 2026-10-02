# Assignment 2 mini POC

This local CLI proves the narrow deterministic flow: workbook validation → candidate selection → Thai PDF rendering → output verification → rejected-row report and manifest. It treats `REQUEST_DOC` as the candidate eligibility rule solely for this POC. The generated letter prominently says it is a test and must not be sent.

Run from `poc/`:

```bash
python3 generate_letters.py ../data/Example\ claim\ table.xlsx
python3 -m pytest -q
```

The output folder name is derived from the source SHA-256, and PDF filenames use worksheet row plus a policy hash to avoid customer data in filenames. Repeating the same input uses the same batch directory and output names. This demonstrates technical repeat detection; production still needs a stable claim/request ID, business-approved wording, an approved font license, access controls, retention, approval and delivery integration.
