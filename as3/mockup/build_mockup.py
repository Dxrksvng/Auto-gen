"""Build a static, clickable Thai mockup of the PROPOSED screens. Nothing here is a working system."""
from pathlib import Path
import html

OUT = Path(__file__).resolve().parent / "screens"
OUT.mkdir(exist_ok=True)
BANNER = "ภาพตัวอย่างหน้าจอ (mockup) — ระบบนี้ยังเป็นข้อเสนอ ยังไม่มีอยู่จริง"

CSS = """
@font-face{font-family:SarabunT;src:url('../../assets/fonts/Sarabun-Regular.ttf');font-weight:400}
@font-face{font-family:SarabunT;src:url('../../assets/fonts/Sarabun-Bold.ttf');font-weight:700}
*{box-sizing:border-box}
body{margin:0;font-family:SarabunT,sans-serif;font-size:18px;line-height:1.45;color:#1d2433;background:#f3f5f9}
.banner{background:#fff4d6;color:#6b4e00;padding:6px 16px;font-size:14px;border-bottom:1px solid #e6d28a}
.top{background:#12306b;color:#fff;padding:10px 16px;font-size:18px;font-weight:700}
.wrap{padding:16px}
.step{display:inline-block;background:#12306b;color:#fff;border-radius:16px;padding:4px 14px 2px;font-size:15px;line-height:1.7;margin-bottom:6px}
h1{font-size:24px;margin:2px 0 10px}
.card{background:#fff;border:1px solid #cfd6e4;border-radius:10px;padding:14px 16px;margin-bottom:12px}
.btn{display:inline-block;background:#1a56db;color:#fff;border-radius:8px;padding:8px 18px;font-weight:700;font-size:18px}
.btn.alt{background:#fff;color:#1a56db;border:2px solid #1a56db}
.btn.off{background:#b8c0d0}
.cards{display:flex;gap:12px}.cards .card{flex:1;margin:0}
.num{font-size:40px;font-weight:700;line-height:1}
.ok{border-top:6px solid #1f8a4c}.bad{border-top:6px solid #c62828}.skip{border-top:6px solid #8a94a6}.warn{border-top:6px solid #d98200}
table{border-collapse:collapse;width:100%;font-size:17px}th,td{border:1px solid #cfd6e4;padding:6px 8px;text-align:left;vertical-align:top}th{background:#eaeff8}
.drop{border:2px dashed #8aa0d0;border-radius:10px;padding:18px;text-align:center;color:#41507a;background:#f7f9fe}
.small{font-size:15px;color:#4a5568}
.grid{table-layout:fixed}.grid td,.grid th{font-size:13px;padding:3px 4px;word-break:break-all}.grid th:first-child{width:24px}.grid th{background:#e2e8f0;text-align:center}.grid .h{background:#d9f0e0}
nav{padding:10px 16px;font-size:14px}nav a{margin-right:10px}
select{font-family:inherit;font-size:18px;padding:6px 10px;width:100%}
"""

def page(name, step, title, body):
    (OUT / f"{name}.html").write_text(f"""<!doctype html><html lang="th"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>{CSS}</style></head><body><div class="banner">{BANNER}</div><div class="top">สร้างจดหมายจาก Excel</div>
<div class="wrap">{f'<span class="step">ขั้นที่ {step}</span>' if step else ''}<h1>{title}</h1>{body}</div></body></html>""", encoding="utf-8")

page("s1_choose", 1, "เลือกประเภทจดหมาย", """
<div class="card"><b>จดหมายขอเอกสารเพิ่มเติม</b><br><span class="small">ใช้กับเคลมที่ต้องขอเอกสารจากลูกค้า &nbsp;|&nbsp; แบบฟอร์มฉบับที่ 1 &nbsp;|&nbsp; เจ้าของ: [TO CONFIRM]</span><br><br><span class="btn">เลือกประเภทนี้</span></div>
<div class="card"><span class="small">ประเภทอื่นจะปรากฏในรายการนี้ เมื่อทีมเจ้าของงานตั้งค่าและผู้อนุมัติอนุมัติแบบฟอร์มแล้วเท่านั้น</span></div>""")

page("s2_download_fill", 2, "ดาวน์โหลดไฟล์ตัวอย่าง แล้วกรอกข้อมูลใน Excel", """
<div class="card"><span class="btn alt">ดาวน์โหลดไฟล์ตัวอย่าง (Excel)</span> &nbsp;<span class="small">กรอก 1 แถวต่อ 1 ลูกค้า</span></div>
<div class="card small"><b>หน้าตาไฟล์ใน Excel</b> (แถวบนสุดคือหัวคอลัมน์ ห้ามแก้)
<table class="grid"><tr><th></th><th>A</th><th>B</th><th>C</th><th>D</th><th>E</th><th>F</th><th>G</th></tr>
<tr><th>1</th><td class="h">customer_name</td><td class="h">policy_number</td><td class="h">coverage_start_date</td><td class="h">coverage_end_date</td><td class="h">hospital_name</td><td class="h">claim_status</td><td class="h">document_request</td></tr>
<tr><th>2</th><td>คุณตัวอย่าง หนึ่ง</td><td>POL-TEST-0001</td><td>2026-01-01</td><td>2026-12-31</td><td>โรงพยาบาลตัวอย่างเอ</td><td>REQUEST_DOC</td><td>["สำเนาใบเสร็จ…"]</td></tr>
<tr><th>3</th><td>…</td><td>…</td><td>…</td><td>…</td><td>…</td><td>…</td><td>…</td></tr></table></div>""")

page("s3_upload", 3, "เลือกไฟล์ที่กรอกแล้ว แล้วกดตรวจไฟล์", """
<div class="card"><div class="drop">ลากไฟล์ Excel มาวางที่นี่ หรือ <b>เลือกไฟล์</b><br><span class="small">ไฟล์ที่เลือก: ขอเอกสารรอบ-ตุลาคม.xlsx</span></div><br><span class="btn">ตรวจไฟล์</span></div>""".replace("ขอเอกสารรอบ-ตุลาคม.xlsx","ขอเอกสารรอบตุลาคม"))

page("s4_result_ok", 4, "ผลการตรวจไฟล์: ไม่มีรายการที่ต้องแก้", """
<div class="cards"><div class="card ok"><div class="num">3</div>พร้อมสร้างจดหมาย</div><div class="card bad"><div class="num">0</div>ต้องแก้ไข</div><div class="card skip"><div class="num">2</div>ไม่ต้องส่งจดหมาย</div></div>
<div class="card">ไฟล์มี <b>5 แถว</b> &nbsp;→&nbsp; 3 + 0 + 2 = 5 &nbsp;<b>ตรงกัน</b><br><br><span class="btn">ดูตัวอย่างจดหมาย</span></div>""")

page("s4b_result_errors", 4, "ผลการตรวจไฟล์: มีรายการที่ต้องแก้", """
<div class="cards"><div class="card ok"><div class="num">1</div>พร้อมสร้างจดหมาย</div><div class="card bad"><div class="num">6</div>ต้องแก้ไข</div><div class="card skip"><div class="num">0</div>ไม่ต้องส่งจดหมาย</div></div>
<div class="card"><table><tr><th>แถวที่</th><th>ช่อง</th><th>ปัญหา</th><th>วิธีแก้</th></tr>
<tr><td>2</td><td>วันสิ้นสุด</td><td>วันสิ้นสุดมาก่อนวันเริ่ม</td><td>แก้วันที่ให้ถูก</td></tr>
<tr><td>3</td><td>สถานะ</td><td>ไม่ตรงที่ระบบรู้จัก</td><td>พิมพ์ให้ตรงตัวอักษร</td></tr>
<tr><td>4</td><td>รายการเอกสาร</td><td>ไม่มีรายการเอกสาร</td><td>ใส่อย่างน้อย 1 รายการ</td></tr></table>
<span class="small">… อีก 3 แถวอยู่ในไฟล์ที่ดาวน์โหลด</span><br><br><span class="btn alt">ดาวน์โหลดรายการที่ต้องแก้</span> &nbsp;<span class="btn off">ดูตัวอย่างจดหมาย</span></div>""")

page("s5_preview", 5, "ดูตัวอย่างจดหมาย 3 ฉบับ แล้วส่งขออนุมัติ", """
<div class="card"><b>ตัวอย่างที่ 1 จาก 3</b> (แถวที่ 2)<br>เรียน คุณ ตัวอย่าง หนึ่ง<br>เรื่อง การแจ้งขอเอกสารเพิ่มเติม<br>… กรมธรรม์เลขที่ POL-TEST-0001 …<br>1. สำเนาใบเสร็จค่ารักษาพยาบาล<br>2. ใบรับรองแพทย์</div>
<div class="card"><b>เช็กก่อนกดส่งขออนุมัติ:</b> ✓ ชื่อและเลขกรมธรรม์ถูกคน &nbsp;✓ วันที่ถูก &nbsp;✓ รายการเอกสารครบ &nbsp;✓ ภาษาไทยอ่านได้ ไม่มีตัวอักษรขาด<br><br><span class="btn">ส่งขออนุมัติ</span> &nbsp;<span class="btn alt">กลับไปแก้ไฟล์</span></div>""")

page("s6_request", 6, "ส่งขออนุมัติ", """
<div class="card">ผู้อนุมัติ<br><select><option>[TO CONFIRM: รายชื่อผู้อนุมัติที่ธุรกิจกำหนด]</option></select><br><br>
ข้อความถึงผู้อนุมัติ (ไม่บังคับ)<br><div class="drop" style="text-align:left">รอบประจำสองสัปดาห์ ตรวจแล้ว 3 ฉบับ</div><br><span class="btn">ส่งขออนุมัติ</span></div>
<div class="card small">ระบบจะบันทึกว่าใครอนุมัติ เวลาใด และใช้แบบฟอร์มฉบับที่เท่าไร</div>""")

page("s7_done", 7, "อนุมัติแล้ว: ดาวน์โหลดจดหมาย", """
<div class="card ok"><b>สร้างจดหมายแล้ว 3 ฉบับ</b> &nbsp;|&nbsp; รหัสรอบงาน: <b>R-ตัวอย่าง-001</b><br><br><span class="btn">ดาวน์โหลดจดหมาย (PDF)</span> &nbsp;<span class="btn alt">ดาวน์โหลดรายงานสรุป</span></div>
<div class="card warn"><b>ยังไม่ได้ส่งถึงลูกค้า</b><br>ระบบนี้สร้างไฟล์ให้เท่านั้น การส่งถึงลูกค้าทำผ่านช่องทางที่ทีมกำหนด [TO CONFIRM]</div>""")

(OUT / "index.html").write_text("<!doctype html><meta charset=utf-8><title>Mockup index</title><nav>" + " ".join(
    f'<a href="{n}.html">{n}</a>' for n in ["s1_choose", "s2_download_fill", "s3_upload", "s4_result_ok", "s4b_result_errors", "s5_preview", "s6_request", "s7_done"]) + "</nav>", encoding="utf-8")
print("built", len(list(OUT.glob("s*.html"))), "screens")
