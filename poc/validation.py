"""Read the claims workbook as text, validate every row and classify it.

Outcome per populated row (exactly one):
  rejected   - at least one error; no letter, listed in the validation report
  skipped    - status is not REQUEST_DOC (a "conflict" if documents are still listed)
  duplicate  - REQUEST_DOC but identical to an earlier row; only the first is generated
  eligible   - becomes one letter

Nothing is guessed: values the rules cannot interpret produce an issue instead.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from openpyxl import load_workbook

from models import DuplicateRow, LetterData, RowIssue, SkippedRow
from normalize import (
    DateError,
    DocumentNames,
    UnknownDocumentError,
    clean_text,
    format_salutation,
    hospital,
    load_document_names,
    parse_date,
    th_date,
)

HEADERS = (
    "customer_name",
    "policy_number",
    "coverage_start_date",
    "coverage_end_date",
    "hospital_name",
    "claim_status",
    "document_request",
)
SHEET_NAME = "Sheet1"
REQUEST_STATUS = "REQUEST_DOC"
OBSERVED_STATUSES = {REQUEST_STATUS, "APPROVED", "REJECTED"}

FIELD_LABELS_TH = {
    "customer_name": "ชื่อลูกค้า",
    "policy_number": "เลขกรมธรรม์",
    "coverage_start_date": "วันเริ่มความคุ้มครอง",
    "coverage_end_date": "วันสิ้นสุดความคุ้มครอง",
    "hospital_name": "ชื่อโรงพยาบาล",
    "claim_status": "สถานะ",
    "document_request": "รายการเอกสาร",
}
_REQUIRED_TEXT_FIELDS = ("customer_name", "policy_number", "hospital_name", "claim_status")


# order matches the ``content`` tuple built in load_and_validate
_CONTENT_LABELS = (
    "customer_name", "policy_number", "coverage_start_date", "coverage_end_date", "hospital_name", "document_request",
)  # fmt: skip


class FileValidationError(ValueError):
    """A problem with the whole file; the batch cannot start."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass
class ValidationResult:
    letters: list[LetterData] = field(default_factory=list)
    issues: list[RowIssue] = field(default_factory=list)
    skipped: list[SkippedRow] = field(default_factory=list)
    duplicates: list[DuplicateRow] = field(default_factory=list)
    rejected_rows: set[int] = field(default_factory=set)
    populated: int = 0

    def counts(self) -> dict[str, int]:
        """Row counts. Invariant: populated = rejected + skipped + duplicates + eligible."""
        return {
            "populated": self.populated,
            "eligible": len(self.letters),
            "rejected": len(self.rejected_rows),
            "skipped": len(self.skipped),
            "conflicts": sum(1 for s in self.skipped if s.conflict),
            "duplicates": len(self.duplicates),
        }


def text_of(value: object) -> str:
    """Cell value as text. Whole-number floats lose the '.0' that Excel adds."""
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return clean_text(str(value))


def _parse_document_list(raw: object) -> list[str] | None:
    """Return the list of names, or None if the cell is not a JSON list of non-empty strings."""
    try:
        parsed = json.loads(text_of(raw))
    except json.JSONDecodeError:
        return None
    if isinstance(parsed, list) and all(isinstance(x, str) and x.strip() for x in parsed):
        return [clean_text(x) for x in parsed]
    return None


def validate_row(source_row: int, row: dict, names: DocumentNames | None = None) -> list[RowIssue]:
    """Return every issue of one row. A row is usable only if no issue has severity "error"."""
    names = names or load_document_names()
    issues: list[RowIssue] = []

    def add(field_name: str, code: str, message: str, severity: str = "error") -> None:
        issues.append(RowIssue(source_row, field_name, code, message, severity))

    for field_name in _REQUIRED_TEXT_FIELDS:
        if not text_of(row[field_name]):
            add(field_name, "REQUIRED", f"ยังไม่ได้กรอก: {FIELD_LABELS_TH[field_name]}")

    parsed_dates = {}
    for field_name in ("coverage_start_date", "coverage_end_date"):
        try:
            parsed_dates[field_name] = parse_date(row[field_name])
        except DateError as exc:
            add(field_name, "INVALID_DATE", f"{FIELD_LABELS_TH[field_name]}: {exc}")
    if len(parsed_dates) == 2 and parsed_dates["coverage_start_date"] > parsed_dates["coverage_end_date"]:
        add(
            "coverage_end_date",
            "DATE_ORDER",
            "วันสิ้นสุดความคุ้มครองอยู่ก่อนวันเริ่มความคุ้มครอง "
            f"(เริ่ม {th_date(parsed_dates['coverage_start_date'])} สิ้นสุด {th_date(parsed_dates['coverage_end_date'])})",
        )

    status = text_of(row["claim_status"])
    if status and status not in OBSERVED_STATUSES:
        add("claim_status", "UNKNOWN_STATUS", f"ไม่รู้จักสถานะ '{status}' ต้องเป็น {', '.join(sorted(OBSERVED_STATUSES))}")

    documents = _parse_document_list(row["document_request"])
    if documents is None:
        add(
            "document_request",
            "INVALID_LIST",
            'รูปแบบรายการเอกสารไม่ถูกต้อง ต้องเป็นรายการในวงเล็บเหลี่ยม เช่น ["ใบรับรองแพทย์","ผลตรวจเลือด"]',
        )
    elif status == REQUEST_STATUS:
        if not documents:
            add("document_request", "REQUIRED_FOR_REQUEST", "สถานะ REQUEST_DOC ต้องมีรายการเอกสารอย่างน้อย 1 รายการ")
        for name in dict.fromkeys(documents):
            try:
                names.resolve(name)
            except UnknownDocumentError:
                add(
                    "document_request",
                    "UNKNOWN_DOCUMENT",
                    f"ไม่พบชื่อเอกสาร '{name}' ในรายการชื่อที่อนุมัติ (config/document_names.yml) "
                    "กรุณาให้เจ้าของแบบฟอร์มกำหนดคำภาษาไทย ระบบไม่พิมพ์ชื่อที่ไม่รู้จักลงในจดหมาย",
                )

    if (
        status == REQUEST_STATUS
        and text_of(row["customer_name"])
        and format_salutation(text_of(row["customer_name"])).warning
    ):
        add(
            "customer_name",
            "NAME_FORMAT",
            "รูปแบบชื่อไม่ตรงรูปแบบที่ระบบรู้จัก (มีตัวเลขหรืออักขระพิเศษ) ระบบคงชื่อตามต้นฉบับ ไม่เติมคำนำหน้า กรุณาตรวจสอบ",
            "warning",
        )
    return issues


def _open_sheet(path: Path):
    try:
        workbook = load_workbook(path, data_only=True, read_only=True)
    except Exception as exc:
        raise FileValidationError("FILE_UNREADABLE", f"เปิดไฟล์ไม่ได้ ไฟล์อาจเสียหรือไม่ใช่ไฟล์ Excel: {exc}") from exc
    if SHEET_NAME not in workbook.sheetnames:
        raise FileValidationError("SHEET_MISSING", f"ไม่พบแผ่นงานชื่อ {SHEET_NAME}")
    return workbook[SHEET_NAME]


def _headers_message(found: tuple) -> str:
    """Say exactly which columns are missing, unknown or out of order, not just what the template is."""
    names = [str(h).strip() for h in found]
    missing = [h for h in HEADERS if h not in names]
    unknown = [h for h in names if h not in HEADERS]
    parts = []
    if missing:
        parts.append(f"ขาดคอลัมน์: {', '.join(missing)}")
    if unknown:
        parts.append(f"มีคอลัมน์ที่ไม่รู้จัก (เกินจากแม่แบบ): {', '.join(unknown)}")
    if not parts:
        parts.append("ลำดับคอลัมน์ไม่ตรงแม่แบบ (ชื่อครบแต่สลับที่หรือซ้ำ)")
    return "หัวคอลัมน์ไม่ตรงกับแม่แบบ " + " · ".join(parts) + f" · แม่แบบคือ: {', '.join(HEADERS)}"


def load_and_validate(path: Path, names: DocumentNames | None = None) -> ValidationResult:
    """Read the workbook, validate every populated row and classify it."""
    names = names or load_document_names()
    rows = _open_sheet(Path(path)).iter_rows(values_only=True)
    try:
        raw_headers = next(rows)
    except StopIteration as exc:
        raise FileValidationError("FILE_EMPTY", "ไฟล์ไม่มีข้อมูล") from exc
    found = tuple(v for v in raw_headers if v is not None)
    if found != HEADERS:
        raise FileValidationError("HEADERS_MISMATCH", _headers_message(found))

    result = ValidationResult()
    first_seen: dict[tuple, int] = {}
    similar_seen: dict[tuple, tuple[int, tuple]] = {}
    for source_row, values in enumerate(rows, start=2):
        values = (tuple(values) + (None,) * len(HEADERS))[: len(HEADERS)]
        if not any(v is not None and v != "" for v in values):
            continue
        result.populated += 1
        row = dict(zip(HEADERS, values, strict=True))
        issues = validate_row(source_row, row, names)
        result.issues.extend(issues)
        if any(i.severity == "error" for i in issues):
            result.rejected_rows.add(source_row)
            continue

        status = text_of(row["claim_status"])
        listed = _parse_document_list(row["document_request"]) or []
        if status != REQUEST_STATUS:
            result.skipped.append(SkippedRow(source_row, f"status={status}", conflict=bool(listed)))
            if listed:
                result.issues.append(
                    RowIssue(
                        source_row,
                        "document_request",
                        "CONFLICTING_ROW",
                        f"ข้อมูลขัดแย้ง ตรวจสอบ: สถานะเป็น {status} แต่มีรายการเอกสาร {len(listed)} รายการ "
                        "ระบบข้ามแถวนี้และไม่สร้างจดหมาย",
                        "warning",
                    )
                )
            continue

        approved = tuple(names.resolve(name) for name in listed)
        policy = text_of(row["policy_number"])
        customer = text_of(row["customer_name"])
        hospital_name = text_of(row["hospital_name"])
        start, end = parse_date(row["coverage_start_date"]), parse_date(row["coverage_end_date"])
        # A duplicate is identical in EVERYTHING the letter prints. Rows that only share policy and documents
        # (for example another hospital) are different letters: both are generated and the later one is flagged.
        content = (customer, policy, start, end, hospital_name, tuple(sorted(approved)))
        if content in first_seen:
            first = first_seen[content]
            result.duplicates.append(DuplicateRow(source_row, first))
            result.issues.append(
                RowIssue(
                    source_row,
                    "policy_number",
                    "DUPLICATE_ROW",
                    f"แถวที่ {source_row} ซ้ำกับแถวที่ {first} (ชื่อ เลขกรมธรรม์ วันที่ โรงพยาบาล และรายการเอกสารเหมือนกันทั้งหมด) "
                    f"สร้างจดหมายเพียงฉบับเดียวจากแถวที่ {first}",
                    "warning",
                )
            )
            continue
        policy_docs = (policy, content[-1])
        if policy_docs in similar_seen:
            earlier_row, earlier = similar_seen[policy_docs]
            differing = [label for label, a, b in zip(_CONTENT_LABELS, earlier, content, strict=True) if a != b]
            result.issues.append(
                RowIssue(
                    source_row,
                    differing[0],
                    "SIMILAR_ROW",
                    f"แถวที่ {source_row} มีเลขกรมธรรม์และรายการเอกสารเหมือนแถวที่ {earlier_row} "
                    f"แต่ต่างกันที่ {', '.join(differing)} ระบบสร้างจดหมายทั้งสองฉบับ ไม่ตัดแถวใดทิ้ง กรุณาตรวจว่าตั้งใจ",
                    "warning",
                )
            )
        else:
            similar_seen[policy_docs] = (source_row, content)
        first_seen[content] = source_row
        result.letters.append(
            LetterData(
                source_row=source_row,
                customer_name=customer,
                salutation=format_salutation(customer).text,
                policy_number=policy,
                coverage_start_date=parse_date(row["coverage_start_date"]),
                coverage_end_date=parse_date(row["coverage_end_date"]),
                hospital_name=hospital_name,
                hospital=hospital(hospital_name),
                requested_documents=approved,
                source_documents=tuple(listed),
            )
        )

    for duplicate_row in result.duplicates:
        result.issues.append(
            RowIssue(
                duplicate_row.duplicate_of,
                "policy_number",
                "DUPLICATE_ROW",
                f"แถวที่ {duplicate_row.duplicate_of} มีแถวซ้ำ: แถวที่ {duplicate_row.source_row}",
                "info",
            )
        )
    result.issues.sort(key=lambda i: (i.source_row, i.code))
    return result
