"""Mimics as2/poc/renderer.py: reportlab Paragraph + TTF (Sarabun instead of Tahoma)."""
import pathlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

here = pathlib.Path(__file__).parent
pdfmetrics.registerFont(TTFont("SarabunT", str(here / "../assets/fonts/Sarabun-Regular.ttf")))
body = ParagraphStyle("b", fontName="SarabunT", fontSize=13, leading=20)
lbl = ParagraphStyle("l", fontName="SarabunT", fontSize=9, leading=12, textColor="#555555")
box = lambda t: Table([[Paragraph(t, body)]], colWidths=[90 * mm], style=TableStyle([("BOX", (0, 0), (-1, -1), 0.3, "#999999")]))
S = [
 ("ชุดทดสอบภาษาไทย (Thai test sheet)", None),
 ("T1 วรรณยุกต์/สระซ้อน", "น้ำ ป้า ปู่ ผู้ป่วย เกี่ยวกับ ขั้นตอน เมื่อ ที่ปรึกษา ผู้รับประโยชน์ กรุณาส่งเอกสาร ปั้นจั่น บ้านป่า ตั๋วเงิน"),
 ("T2 ประโยคยาวไม่มีเว้นวรรค ในกล่องแคบ 90 มม.", ("box", "จากการตรวจสอบรายละเอียดข้อมูลการเคลมจากทางโรงพยาบาลบำรุงราษฎร์อินเตอร์เนชั่นแนลซึ่งเอาประกันภัยตามกรมธรรม์ดังกล่าวบริษัทมีความจำเป็นต้องให้ท่านส่งเอกสารเพิ่มเติมดังนี้")),
 ("T3 ไทยปนอังกฤษและตัวเลข", "เลขกรมธรรม์ POL-2026-000123 ขอ Medical Report และสำเนาใบเสร็จ 2 ฉบับ (ภายใน 30 วัน)"),
 ("T4 เลขไทย และวันที่ พ.ศ.", "๒ ตุลาคม ๒๕๖๙ / 02/10/2569 / 2 ต.ค. 2569"),
 ("T5 ชื่อโรงพยาบาลยาวในกล่องแคบ", ("box", "โรงพยาบาลมหาวิทยาลัยเทคโนโลยีสุรนารีเฉลิมพระเกียรติและศูนย์การแพทย์เฉพาะทางโรคหัวใจ")),
 ("T6 อักขระพิเศษ ๆ ฯ ฤ ฦ ำ", "กรุงเทพฯ ดีๆ ฤๅษี ฦๅ นำ ทำ จำ คำ"),
 ("T7 รายการเอกสารยาวในกล่องแคบ", ("box", "1. สำเนาใบเสร็จรับเงินค่ารักษาพยาบาลฉบับจริงพร้อมรายละเอียดค่าใช้จ่ายทุกรายการ<br/>2. รายงานผลการตรวจทางห้องปฏิบัติการ")),
]
story = []
for label, content in S:
    if content is None:
        story += [Paragraph(label, ParagraphStyle("h", parent=body, fontSize=15)), Spacer(1, 4 * mm)]
        continue
    story.append(Paragraph(label, lbl))
    story.append(box(content[1]) if isinstance(content, tuple) else Paragraph(content, body))
    story.append(Spacer(1, 3 * mm))
SimpleDocTemplate(str(here / "out_reportlab.pdf"), pagesize=A4, leftMargin=20 * mm, topMargin=20 * mm).build(story)
print("reportlab ok")
