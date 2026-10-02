"""Build docs/examples/messy_example.xlsx: one row for each way a row can be classified.

The file is fictional test data (no real customers). It exists so the answer can show a
real validation report and so a test keeps that report from going stale.
"""

from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.utils.datetime import to_excel

HEADERS = (
    "customer_name", "policy_number", "coverage_start_date", "coverage_end_date",
    "hospital_name", "claim_status", "document_request",
)  # fmt: skip
TARGET = Path(__file__).resolve().parents[2] / "docs" / "examples" / "messy_example.xlsx"


def rows() -> list[list]:
    d = datetime  # noqa: DTZ001 - naive datetimes are what Excel stores
    return [
        # row 2: normal request, English document name is mapped to Thai
        ["สมชาย ใจดี", "DEMO-001", d(2026, 1, 1), d(2026, 12, 31), "กรุงเทพ", "REQUEST_DOC", '["Medical Report"]'],
        # row 3: identical to row 2 -> duplicate, only row 2 is generated
        ["สมชาย ใจดี", "DEMO-001", d(2026, 1, 1), d(2026, 12, 31), "กรุงเทพ", "REQUEST_DOC", '["Medical Report"]'],
        # row 4: approved but documents listed -> skipped and listed as a conflict
        ["คุณสมหญิง รักดี", "DEMO-002", d(2026, 2, 1), d(2027, 1, 31), "รพ.บำรุงราษฎร์", "APPROVED", '["ใบรับรองแพทย์"]'],
        # row 5: unknown document name -> rejected (UNKNOWN_DOCUMENT)
        ["นายวิชัย พัฒนาดี", "DEMO-003", d(2026, 3, 1), d(2027, 2, 28), "สมิติเวช", "REQUEST_DOC", '["Discharge Summary"]'],
        # row 6: end before start -> rejected (DATE_ORDER)
        ["คุณนภัสสร แสงทอง", "DEMO-004", d(2027, 4, 1), d(2026, 3, 31), "พระรามเก้า", "REQUEST_DOC", '["ใบรับรองแพทย์"]'],
        # row 7: Excel serial-number dates -> converted and generated
        ["กิตติศักดิ์ มีสุข", "DEMO-005", to_excel(d(2026, 5, 10)), to_excel(d(2027, 5, 9)), "ศิริราช", "REQUEST_DOC",
         '["ผลตรวจทางห้องปฏิบัติการ","สำเนาประวัติการรักษา"]'],
        # row 8: name with a digit -> generated, but with a NAME_FORMAT warning
        ["ธนกร 2", "DEMO-006", d(2026, 7, 1), d(2027, 6, 30), "เมดพาร์ค", "REQUEST_DOC", '["ใบรับรองแพทย์"]'],
        # row 9: rejected status without documents -> plain skip
        ["คุณอรทัย วัฒนดี", "DEMO-007", d(2026, 8, 15), d(2027, 8, 14), "รามาธิบดี", "REJECTED", "[]"],
        # row 10: document list is not a list -> rejected (INVALID_LIST)
        ["คุณภาคภูมิ ตั้งใจ", "DEMO-008", d(2026, 9, 1), d(2027, 8, 31), "ธนบุรี", "REQUEST_DOC", "ใบรับรองแพทย์"],
    ]


def build(path: Path = TARGET) -> Path:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Sheet1"
    sheet.append(list(HEADERS))
    for row in rows():
        sheet.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(path)
    return path


if __name__ == "__main__":
    print(build())
