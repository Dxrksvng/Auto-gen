# Assignment 3 — Platform model

> **หมายเหตุ (2 ต.ค. 2569):** เอกสารนี้เป็นฉบับก่อนการเขียน A3 ใหม่ คำตอบหลักอยู่ที่ `ANSWER.md` ข้อความที่ขัดกับสถานะจริงของ A2 ถูกแก้แล้ว รายละเอียดการตรวจอยู่ที่ `docs/A2_A3_CONSISTENCY.md`


## The abstraction

The migration from a single workflow to a platform begins by separating common capabilities from document-specific variation.

| Shared platform capability | Variable by document type |
| --- | --- |
| File intake, batch/job status, validation framework, preview, PDF rendering, output checks, error reporting, audit and version references | Input schema, source mapping, validation constraints, bounded business rules, template, review policy, output naming/policy |

The shared engine executes a Document Definition; it should not grow a long `if document_type == …` branch for every team.

```text
                         Shared document engine
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
  Definition: request letter  Definition: renewal notice  Definition: warning letter
       schema/template/rules        schema/template/rules       schema/template/rules
```

This design makes a supported new document type a governed configuration and test exercise. A requirement that cannot fit the supported contract is an explicit engineering extension request, rather than a hidden exception in shared code.

## Platform boundary

Centralization is appropriate where workflows share a batch-in, validate, render, review and release pattern. A workflow that requires fundamentally different input, rendering, timing or integrations should remain outside the platform or drive a reviewed extension.
