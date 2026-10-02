"""Build the two downloadable sample Excel files for the user guide.

All names/numbers are obviously fictional. Header names and the sheet name
are copied from as2/poc/validation.py (HEADERS, "Sheet1") so the files can be
read by the real A2 validator. Second sheet is Thai help text; A2 ignores it.

Run: uv run --with openpyxl python scripts/build_sample_excel.py
"""
import ast
import sys
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent.parent
A2_VALIDATION = ROOT.parent / "as2" / "poc" / "validation.py"
OUT = ROOT / "examples"


def read_a2_headers() -> tuple[str, ...]:
    tree = ast.parse(A2_VALIDATION.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "HEADERS":
            return tuple(ast.literal_eval(node.value))
    raise SystemExit("HEADERS not found in as2/poc/validation.py")


HEADERS = read_a2_headers()
D = datetime
GOOD = [
    ["คุณตัวอย่าง หนึ่ง", "POL-DEMO-0001", D(2026, 1, 1), D(2026, 12, 31), "โรงพยาบาลตัวอย่าง เอ", "REQUEST_DOC", '["สำเนาใบเสร็จค่ารักษาพยาบาล","ใบรับรองแพทย์"]'],
    ["คุณตัวอย่าง สอง", "POL-DEMO-0002", D(2026, 2, 1), D(2027, 1, 31), "โรงพยาบาลตัวอย่าง บี", "APPROVED", "[]"],
    ["คุณตัวอย่าง สาม", "POL-DEMO-0003", D(2026, 3, 15), D(2027, 3, 14), "โรงพยาบาลตัวอย่าง ซี", "REQUEST_DOC", '["ผลตรวจทางห้องปฏิบัติการ"]'],
    ["คุณตัวอย่าง สี่", "POL-DEMO-0004", D(2026, 4, 1), D(2027, 3, 31), "โรงพยาบาลตัวอย่าง เอ", "REQUEST_DOC", '["สำเนาประวัติการรักษา","ใบรับรองแพทย์","สำเนาใบเสร็จค่ารักษาพยาบาล"]'],
    ["คุณตัวอย่าง ห้า", "POL-DEMO-0005", D(2026, 5, 10), D(2027, 5, 9), "โรงพยาบาลตัวอย่าง ดี", "REJECTED", "[]"],
]
# Practice file: Excel rows 4, 6 and 7 are wrong on purpose (header is row 1; verified with as2 load_and_validate).
PRACTICE = [
    GOOD[0],
    GOOD[1],
    ["คุณตัวอย่าง สาม", "POL-DEMO-0003", D(2026, 3, 15), D(2027, 3, 14), "", "REQUEST_DOC", '["ผลตรวจทางห้องปฏิบัติการ"]'],
    GOOD[3],
    ["คุณตัวอย่าง ห้า", "POL-DEMO-0005", D(2027, 5, 9), D(2026, 5, 10), "โรงพยาบาลตัวอย่าง ดี", "REQUEST_DOC", '["ใบรับรองแพทย์"]'],
    ["คุณตัวอย่าง หก", "POL-DEMO-0006", D(2026, 6, 1), D(2027, 5, 31), "โรงพยาบาลตัวอย่าง อี", "REQUEST_DOC", "ใบรับรองแพทย์"],
]
HELP = [
    ("หัวคอลัมน์ (ห้ามเปลี่ยน)", "ใส่อะไร", "ตัวอย่าง"),
    ("customer_name", "ชื่อลูกค้า รวมคำนำหน้า", "คุณตัวอย่าง หนึ่ง"),
    ("policy_number", "เลขกรมธรรม์", "POL-DEMO-0001"),
    ("coverage_start_date", "วันเริ่มความคุ้มครอง ต้องเป็นวันที่ใน Excel", "2026-01-01"),
    ("coverage_end_date", "วันสิ้นสุดความคุ้มครอง ต้องไม่ก่อนวันเริ่ม", "2026-12-31"),
    ("hospital_name", "ชื่อโรงพยาบาล", "โรงพยาบาลตัวอย่าง เอ"),
    ("claim_status", "เลือกจากรายการ: REQUEST_DOC = ต้องขอเอกสารเพิ่ม, APPROVED = อนุมัติแล้ว, REJECTED = ไม่อนุมัติ", "REQUEST_DOC"),
    ("document_request", "รายการเอกสารที่ขอ เขียนในวงเล็บเหลี่ยม ชื่อแต่ละอย่างอยู่ในเครื่องหมายคำพูด คั่นด้วยจุลภาค ถ้าไม่ขอให้พิมพ์ []", '["ใบรับรองแพทย์","ผลตรวจเลือด"]'),
    ("", "", ""),
    ("หมายเหตุ", "ข้อมูลในไฟล์นี้เป็นข้อมูลสมมติเพื่อฝึกใช้งาน ไม่ใช่ลูกค้าจริง ระบบอ่านเฉพาะแผ่นงานชื่อ Sheet1", ""),
]


def build(path: Path, rows: list, blank_rows_for_template: int = 0) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(list(HEADERS))
    for r in rows:
        ws.append(r)
    for c in ws[1]:
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor="DFF0F2")
    for col, w in zip("ABCDEFG", (24, 18, 18, 18, 26, 16, 60)):
        ws.column_dimensions[col].width = w
    for row in ws.iter_rows(min_row=2, min_col=3, max_col=4):
        for c in row:
            c.number_format = "yyyy-mm-dd"
    dv = DataValidation(type="list", formula1='"REQUEST_DOC,APPROVED,REJECTED"', allow_blank=False)
    dv.error = "เลือกค่าจากรายการเท่านั้น"
    ws.add_data_validation(dv)
    dv.add("F2:F200")
    ws.freeze_panes = "A2"
    h = wb.create_sheet("คำอธิบาย")
    for row in HELP:
        h.append(list(row))
    for c in h[1]:
        c.font = Font(bold=True)
    h.column_dimensions["A"].width = 26
    h.column_dimensions["B"].width = 80
    h.column_dimensions["C"].width = 36
    for row in h.iter_rows():
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    wb.save(path)


def main() -> int:
    OUT.mkdir(exist_ok=True)
    targets = {
        "ตัวอย่างขอเอกสารเพิ่มเติม.xlsx": GOOD,
        "ไฟล์ฝึกแก้ไข.xlsx": PRACTICE,
        "แม่แบบขอเอกสารเพิ่มเติม.xlsx": [],
    }
    for name, rows in targets.items():
        build(OUT / name, rows)
        print("wrote", OUT / name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
