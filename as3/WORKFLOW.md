# Assignment 3 — Workflows

> **หมายเหตุ (2 ต.ค. 2569):** เอกสารนี้เป็นฉบับก่อนการเขียน A3 ใหม่ คำตอบหลักอยู่ที่ `ANSWER.md` ข้อความที่ขัดกับสถานะจริงของ A2 ถูกแก้แล้ว รายละเอียดการตรวจอยู่ที่ `docs/A2_A3_CONSISTENCY.md`


## Normal operator workflow

```text
Choose document type → download its Excel template → fill one row per record
→ upload → inspect row errors → preview → request/review approval → generate/release
```

The downloadable input template establishes the expected headers and reduces accidental schema drift. Validation reports the row, field, problem and corrective action, rather than exposing technical exception names.

## New document type onboarding

```text
Business requirement → define schema → create approved template → map fields
→ define bounded validation/rules → test sample data → review → publish
```

This is intentionally distinct from the normal workflow. Operators should never rebuild mappings and business logic for every batch.

## Optional AI assistance

During onboarding, an AI assistant may suggest mappings between spreadsheet headers and template placeholders, then identify potential mismatches. A human reviews the suggestion and the platform runs deterministic tests before saving a published definition. The assistant does not publish configuration or generate unconstrained customer wording at runtime.
