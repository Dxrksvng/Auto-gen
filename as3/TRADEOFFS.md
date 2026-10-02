# Assignment 3 — Trade-offs

> **หมายเหตุ (2 ต.ค. 2569):** เอกสารนี้เป็นฉบับก่อนการเขียน A3 ใหม่ คำตอบหลักอยู่ที่ `ANSWER.md` ข้อความที่ขัดกับสถานะจริงของ A2 ถูกแก้แล้ว รายละเอียดการตรวจอยู่ที่ `docs/A2_A3_CONSISTENCY.md`


| Area | Benefit | Cost or risk | Response |
| --- | --- | --- | --- |
| Reuse | Build rendering, validation and reporting once | A shared defect can affect more teams | Versioning, tests, staged release and recovery plan |
| Onboarding | Supported document types avoid a separate application | Definitions and templates still need design and testing | Keep the contract small and provide examples |
| Consistency | Similar checks, statuses and user experience | Unusual workflows can feel constrained | Use reviewed extensions; do not force every PDF into the platform |
| Governance | Traceable versions and controlled release | Publishing is slower than editing a local script | Match review rigor to change risk |
| Operations | Platform fixes benefit several teams | Shared ownership, migration and support cost | Start with a pilot and expand on proven common patterns |
| Flexibility | Teams can vary inputs and templates | A powerful configuration language becomes hidden code | Support bounded declarative rules only |

The choice is justified only when several workflows actually share the same core path. Centralization creates reuse and shared blast radius at the same time; both need to be made explicit.
