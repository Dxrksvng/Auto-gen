# Assignment 3 — Evidence and open questions

> **หมายเหตุ (2 ต.ค. 2569):** เอกสารนี้เป็นฉบับก่อนการเขียน A3 ใหม่ คำตอบหลักอยู่ที่ `ANSWER.md` ข้อความที่ขัดกับสถานะจริงของ A2 ถูกแก้แล้ว รายละเอียดการตรวจอยู่ที่ `docs/A2_A3_CONSISTENCY.md`


## Facts from the assignment

- Assignment 2 has been successful for three months.
- Several teams want to use it.
- Teams differ in templates, data and business requirements.
- The target system generates different documents from Excel data.
- The prompt gives warning letters, renewal notices and pre-existing condition confirmations as examples.
- The user guide targets nontechnical staff familiar with Microsoft Office, Google Workspace and email.

## Facts from Assignment 2 evidence

- The A2 code (`../as2/poc/`) validates Excel data, renders a hardcoded POC Thai letter (not the supplied template) and checks PDF text. Preview, human approval and controlled release appear only in the text of `../as2/ANSWER.md`, not in the code. There is no audit log, access control or template registry in A2 code.
- AS2 deliberately leaves actual wording, owner roles, delivery method and further business rules for stakeholder confirmation.

## Proposed design

Document Definition, document catalog, schema/template registry, immutable versions, draft-to-published lifecycle, batch model, access boundaries and optional onboarding assistance are design proposals. They are not claims about Sunday systems.

## Open questions

1. Which document types should be piloted first, and what common path do they share?
2. Who owns templates, rules and publication for each type?
3. Which changes require business approval?
4. What batch size, completion time and concurrency are expected?
5. Which access scopes, retention rules and delivery channels apply?
6. Is a stable upstream request identifier available for idempotency, as AS2 recommended?
7. Which workflows have input, timing or integrations that make them unsuitable for this platform?
