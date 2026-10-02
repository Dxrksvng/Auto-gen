# Assignment 3 — Governance and change control

> **หมายเหตุ (2 ต.ค. 2569):** เอกสารนี้เป็นฉบับก่อนการเขียน A3 ใหม่ คำตอบหลักอยู่ที่ `ANSWER.md` ข้อความที่ขัดกับสถานะจริงของ A2 ถูกแก้แล้ว รายละเอียดการตรวจอยู่ที่ `docs/A2_A3_CONSISTENCY.md`


Centralization raises the blast radius of shared failures. Safe reuse therefore requires a visible lifecycle:

```text
Draft → Test with sample data → Review → Published → Retired
```

Before publication, validate the schema, mapping completeness, supported rules, template placeholders, representative rendered output and required business approval. For Thai documents, A2 has no font check beyond raising an error when no font file is found (`../as2/poc/renderer.py:21-26`); the visual check was manual. A3 proposes a Thai test sheet and an allowed-font list instead (see `ANSWER.md` 3.2.2).

Treat content, schema, rule and shared-engine changes separately because they have different blast radius. Do not overwrite a production template or definition: publish `v2`, retain `v1` for history, and roll new jobs back to the known-good version when needed. Historical jobs continue to reference the version actually used.

Production access boundaries should distinguish people who run jobs, configure drafts, publish changes and administer the platform. Exact roles need business agreement; no Sunday role model is assumed. Audit events should cover configuration publication, batch creation, generation outcome and release without logging sensitive document content unnecessarily.
