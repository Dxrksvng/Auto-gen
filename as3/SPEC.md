# Assignment 3 — System design specification

> **หมายเหตุ (2 ต.ค. 2569):** เอกสารนี้เป็นฉบับก่อนการเขียน A3 ใหม่ คำตอบหลักอยู่ที่ `ANSWER.md` ข้อความที่ขัดกับสถานะจริงของ A2 ถูกแก้แล้ว รายละเอียดการตรวจอยู่ที่ `docs/A2_A3_CONSISTENCY.md`


## Problem

After three successful months of the Assignment 2 workflow, several teams want to produce different PDFs from Excel data. Their template, data shape and business requirements differ. Building a separate application per team would duplicate the same intake, validation, rendering, review and audit work (of which only validation, rendering and a run summary exist in A2 code; intake UI, review and audit do not).

## Proposed product

A centralized Document Automation Platform provides a catalog of approved document types. Each type is represented by a published, versioned **Document Definition**. The platform executes the definition against an uploaded batch.

## Functional requirements

1. Users select an approved document type and download its input workbook.
2. The platform validates the file and each row before rendering.
3. It maps source columns to stable document fields, applies bounded rules, renders a preview, and generates PDFs for valid rows.
4. It exposes record-level errors in business language and records a batch manifest.
5. Every batch records its Document Definition and template versions.
6. Configuration changes follow a draft, test, review and publish lifecycle. Normal operators run published definitions only.

## Non-functional requirements

The design needs reusable shared capabilities, isolation between teams, maintainable change paths, traceability, safe failure behavior and a nontechnical operator experience. It must not turn template configuration into executable code.

## Scope boundary

The POC demonstrates two or three representative document definitions with different schemas and templates using one engine. Production may add access control, durable jobs, auditing, storage, monitoring, integrations and notifications when validated operating needs justify them.
