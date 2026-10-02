# Assignment 3 — Document Definition contract

> **หมายเหตุ (2 ต.ค. 2569):** เอกสารนี้เป็นฉบับก่อนการเขียน A3 ใหม่ คำตอบหลักอยู่ที่ `ANSWER.md` ข้อความที่ขัดกับสถานะจริงของ A2 ถูกแก้แล้ว รายละเอียดการตรวจอยู่ที่ `docs/A2_A3_CONSISTENCY.md`

> Real example: `examples/definitions/request_documents.v1.yaml` (cross-checked against A2 code). The YAML below is the older illustrative sketch.

A Document Definition is controlled configuration that describes one document type. It provides flexibility without permitting arbitrary behavior.

```yaml
# Illustrative only; this is not Sunday data or policy.
id: renewal_notice
version: 3
metadata:
  display_name: Renewal Notice
  status: published
input:
  schema_version: renewal_input_v2
template:
  id: renewal_notice
  version: 5
mapping:
  customer_name: source.customer_name
  reference_number: source.reference_number
validation:
  required: [customer_name, reference_number]
approval:
  mode: preview_before_release
output:
  format: pdf
```

| Component | Responsibility |
| --- | --- |
| Metadata | Identifier, display name, owner, lifecycle and version |
| Input schema | Expected headers, types and required source fields |
| Mapping | Converts source columns into stable document fields |
| Validation | Deterministic field and cross-field checks |
| Business rules | Supported declarative conditions, separated from visual layout |
| Template reference | Approved template and its immutable version |
| Approval/output policy | Required review point and controlled result behavior |

Published definitions are immutable. Later revisions create a new version, so a historical batch can be traced to the exact schema, template and rules used. The configuration boundary excludes executable code, direct database access, arbitrary file paths and arbitrary outbound calls.
