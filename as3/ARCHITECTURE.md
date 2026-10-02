# Assignment 3 — Architecture

> **หมายเหตุ (2 ต.ค. 2569):** เอกสารนี้เป็นฉบับก่อนการเขียน A3 ใหม่ คำตอบหลักอยู่ที่ `ANSWER.md` ข้อความที่ขัดกับสถานะจริงของ A2 ถูกแก้แล้ว รายละเอียดการตรวจอยู่ที่ `docs/A2_A3_CONSISTENCY.md`


## Main path

```text
Business user
  │ select a published type / upload Excel
  v
Document catalog ───────> Document Definition registry
  │                              │ schema, mapping, rules, template, policy
  v                              v
Upload and job service ──> validation engine ──> normalized document model
                                      │                    │
                          row error report                  v
                                                     template renderer
                                                            │
                                                            v
                                               PDF checks → preview → approved batch output
                                                            │
                                                            v
                                                     batch manifest
```

Shared cross-cutting concerns are access boundaries, version history, batch status, audit events, storage, logs and operational alerts. These belong beside the flow so that teams receive consistent controls rather than custom implementations.

## Control plane and execution plane

The **control plane** manages schemas, templates, mappings, rules and publication. The **execution plane** runs uploaded batches using an already published definition. This prevents an operator who is creating documents from unintentionally modifying system behavior.

For a small POC, the execution may be synchronous. If measured job duration or volume requires it, production can use a job service, queue, workers and durable storage. The architecture does not assume those components before evidence supports them.

## Isolation

Jobs pin an explicit published definition version. Team A's template or rule changes cannot silently change Team B's job because each has separate definitions, explicit references and pre-publication checks.
