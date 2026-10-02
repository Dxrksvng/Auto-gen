from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from models import LetterData


TEMPLATE_VERSION = "poc-th-v1"
FONT_CANDIDATES = (
    Path("/System/Library/Fonts/Supplemental/Tahoma.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
)


def _register_font() -> str:
    for path in FONT_CANDIDATES:
        if path.exists():
            pdfmetrics.registerFont(TTFont("ThaiPOC", str(path)))
            return "ThaiPOC"
    raise RuntimeError("No Thai-capable font found; configure an approved embeddable font")


def render_letter(letter: LetterData, output_path: Path) -> None:
    font = _register_font()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(".tmp.pdf")
    styles = getSampleStyleSheet()
    body = ParagraphStyle("ThaiBody", parent=styles["BodyText"], fontName=font, fontSize=12, leading=20, spaceAfter=5)
    title = ParagraphStyle("ThaiTitle", parent=body, alignment=TA_CENTER, fontSize=14, leading=22)
    date = lambda value: value.strftime("%d/%m/%Y")
    story = [
        Paragraph("ตัวอย่างเพื่อการทดสอบ — ห้ามส่งลูกค้า", title),
        Spacer(1, 7 * mm),
        Paragraph(f"เรียน คุณ {letter.customer_name}", body),
        Paragraph("เรื่อง การแจ้งขอเอกสารเพิ่มเติม", body),
        Spacer(1, 4 * mm),
        Paragraph(
            f"ตามข้อมูลตัวอย่าง กรมธรรม์เลขที่ {letter.policy_number} มีความคุ้มครองตั้งแต่วันที่ "
            f"{date(letter.coverage_start_date)} ถึงวันที่ {date(letter.coverage_end_date)}", body
        ),
        Paragraph(f"จากข้อมูลการเคลมของโรงพยาบาล {letter.hospital_name} กรุณาตรวจสอบรายการเอกสารเพิ่มเติมดังนี้", body),
    ]
    for index, document in enumerate(letter.requested_documents, start=1):
        story.append(Paragraph(f"{index}. {document}", body))
    story.extend([
        Spacer(1, 8 * mm),
        Paragraph("ข้อความนี้เป็น POC จาก template ที่ยังไม่ได้รับการยืนยันทางธุรกิจ", body),
    ])
    document = SimpleDocTemplate(str(tmp_path), pagesize=A4, rightMargin=24 * mm, leftMargin=24 * mm, topMargin=20 * mm, bottomMargin=20 * mm)
    document.build(story)
    tmp_path.replace(output_path)

