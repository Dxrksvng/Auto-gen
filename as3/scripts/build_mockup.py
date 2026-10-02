"""Build the static, clickable Thai mockup and take PNG screenshots.

Status labels and messages come from docs/message-catalog.json so the mockup,
the user guide and the check scripts use the same words. All data on the
screens is fictional. The platform is a PROPOSAL; every screen carries a
"mockup" ribbon.

Run: python3 scripts/build_mockup.py
"""
import html
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAT = json.loads((ROOT / "docs" / "message-catalog.json").read_text(encoding="utf-8"))
MSG = {m["id"]: m for m in CAT["messages"]}
CHIP = {c["id"]: c["label_th"] for c in CAT["row_chips"] + CAT["run_chips"]}
OUT = ROOT / "mockup"
IMG = ROOT / "docs" / "guide-images"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONT_DIR = "../docs/rendering-test/.fonts"

e = html.escape

CSS = f"""
@font-face {{ font-family: S; src: url('{FONT_DIR}/Sarabun-Regular.ttf'); font-weight: 400; }}
@font-face {{ font-family: S; src: url('{FONT_DIR}/Sarabun-Bold.ttf'); font-weight: 700; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: S, Tahoma, sans-serif; font-size: 18px; line-height: 1.55; background: #EEF2F5; color: #15212B; }}
.ribbon {{ background: #FFF0D2; color: #7A4A00; padding: 6px 20px; font-size: 14px; border-bottom: 1px solid #E5C98B; }}
.top {{ background: #0B6E78; color: #fff; padding: 14px 24px; display: flex; justify-content: space-between; align-items: center; }}
.top b {{ font-size: 20px; }} .top span {{ font-size: 15px; opacity: .9; }}
.wrap {{ max-width: 1080px; margin: 22px auto; padding: 0 24px; }}
.steps {{ display: flex; gap: 8px; margin-bottom: 18px; font-size: 15px; }}
.steps div {{ flex: 1; padding: 8px 10px; border-radius: 8px; background: #fff; border: 1px solid #D5DCE2; color: #55626E; text-align: center; }}
.steps div.on {{ background: #0B6E78; color: #fff; border-color: #0B6E78; font-weight: 700; }}
.card {{ background: #fff; border: 1px solid #D5DCE2; border-radius: 12px; padding: 24px 28px; margin-bottom: 16px; }}
h1 {{ font-size: 26px; margin: 0 0 6px; }} h2 {{ font-size: 20px; margin: 0 0 10px; }} p {{ margin: 6px 0 12px; }}
.muted {{ color: #55626E; font-size: 16px; }}
.btn {{ display: inline-block; background: #0B6E78; color: #fff; padding: 12px 24px; border-radius: 8px; font-weight: 700; text-decoration: none; border: 0; font-size: 18px; font-family: inherit; }}
.btn.sec {{ background: #fff; color: #0B6E78; border: 2px solid #0B6E78; }}
.btn.warn {{ background: #A02A2A; }}
.grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
.doc {{ border: 2px solid #0B6E78; border-radius: 12px; padding: 18px 20px; }}
.doc.off {{ border: 2px dashed #B9C2CA; color: #8A96A1; }}
.chip {{ display: inline-block; padding: 2px 12px; border-radius: 999px; font-size: 15px; font-weight: 700; }}
.c-READY {{ background: #DFF0F2; color: #0B5560; }} .c-FIX {{ background: #FADFDF; color: #8A1F1F; }}
.c-SKIP {{ background: #E9EDF0; color: #55626E; }} .c-DONE {{ background: #DCF2E5; color: #1D7447; }}
.c-FAILED {{ background: #FADFDF; color: #8A1F1F; }} .c-DUP {{ background: #FFF0D2; color: #7A4A00; }}
.c-WAIT_APPROVAL {{ background: #FFF0D2; color: #7A4A00; }} .c-APPROVED {{ background: #DCF2E5; color: #1D7447; }}
.c-NOT_APPROVED {{ background: #FADFDF; color: #8A1F1F; }} .c-STOP_FILE {{ background: #FADFDF; color: #8A1F1F; }}
.counts {{ display: flex; gap: 14px; margin: 10px 0 4px; flex-wrap: wrap; }}
.count {{ border: 1px solid #D5DCE2; border-radius: 10px; padding: 10px 18px; min-width: 150px; }}
.count b {{ font-size: 28px; display: block; line-height: 1.1; }}
table {{ border-collapse: collapse; width: 100%; font-size: 16px; }}
th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #E1E6EA; vertical-align: top; }}
th {{ background: #F3F6F8; font-size: 14px; color: #55626E; }}
td:first-child {{ white-space: nowrap; }}
.drop {{ border: 2px dashed #7FA9AE; background: #F1F8F8; border-radius: 12px; padding: 28px; text-align: center; }}
.letter {{ background: #fff; border: 1px solid #C9D1D8; padding: 26px 34px; font-size: 16px; line-height: 1.8; box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
.grid2 {{ display: grid; grid-template-columns: 1.15fr 1fr; gap: 18px; }}
label {{ display: block; margin: 10px 0 4px; font-weight: 700; font-size: 16px; }}
.field {{ border: 1px solid #B9C2CA; border-radius: 8px; padding: 10px 12px; background: #fff; }}
.sheet td, .sheet th {{ border: 1px solid #C9D1D8; padding: 6px 10px; font-size: 15px; white-space: nowrap; }}
.sheet th {{ background: #E6EDF3; color: #15212B; }} .sheet td.n {{ background: #F3F6F8; color: #55626E; text-align: center; width: 36px; }}
.err {{ background: #FFF0D2; }}
nav.index a {{ display: block; padding: 6px 0; color: #0B6E78; }}
"""

STEPS = ["1 เลือกเอกสาร", "2 ดาวน์โหลดแม่แบบ", "3 กรอกข้อมูล", "4 อัปโหลด", "5 ตรวจและขออนุมัติ", "6 รับจดหมาย"]


def chip(cid: str) -> str:
    return f'<span class="chip c-{cid}">{e(CHIP[cid])}</span>'


def page(title: str, active: int, body: str, nxt: str = "") -> str:
    steps = "".join(f'<div class="{"on" if i == active else ""}">{e(s)}</div>' for i, s in enumerate(STEPS)) if active >= 0 else ""
    return f"""<!doctype html><html lang="th"><meta charset="utf-8"><title>{e(title)}</title>
<style>{CSS}</style>
<div class="ribbon">ภาพตัวอย่างหน้าจอ (mockup) ระบบนี้ยังเป็นข้อเสนอ ข้อมูลทั้งหมดเป็นข้อมูลสมมติ</div>
<div class="top"><b>ระบบสร้างเอกสารจากไฟล์ Excel</b><span>ทีม: ตัวอย่าง &nbsp;|&nbsp; ผู้ใช้: ผู้ใช้ตัวอย่าง</span></div>
<div class="wrap"><div class="steps">{steps}</div>{body}{nxt}
<p class="muted"><a href="index.html">กลับหน้ารวมภาพตัวอย่าง</a></p></div></html>"""


def mock_sheet(rows, bad=()):
    head = ["customer_name", "policy_number", "coverage_start_date", "coverage_end_date", "hospital_name", "claim_status", "document_request"]
    t = "<table class='sheet'><tr><th></th>" + "".join(f"<th>{h}</th>" for h in head) + "</tr>"
    for i, r in enumerate(rows, start=2):
        t += f"<tr><td class='n'>{i}</td>" + "".join(f"<td class='{'err' if (i, j) in bad else ''}'>{e(str(c))}</td>" for j, c in enumerate(r)) + "</tr>"
    return t + "</table>"


LETTER = """<div class="letter"><b>เรียน</b> คุณตัวอย่าง หนึ่ง<br><b>เรื่อง</b> การแจ้งขอเอกสารเพิ่มเติม<br><br>
ตามที่ท่านได้ทำประกันสุขภาพ กรมธรรม์เลขที่ POL-DEMO-0001 โดยความคุ้มครองมีผลตั้งแต่วันที่ [วันที่เริ่ม] ถึงวันที่ [วันที่สิ้นสุด] นั้น
จากการตรวจสอบข้อมูลการเคลมจากทางโรงพยาบาลตัวอย่าง เอ บริษัทมีความจำเป็นต้องให้ท่านส่งเอกสารเพิ่มเติม ดังนี้<br>
&nbsp;&nbsp;1. สำเนาใบเสร็จค่ารักษาพยาบาล<br>&nbsp;&nbsp;2. ใบรับรองแพทย์<br><br>
<span style="color:#7A4A00;font-size:14px">ตัวอย่างข้อความ ถ้อยคำจริงต้องเป็นฉบับที่ผู้รับผิดชอบอนุมัติแล้ว [TO CONFIRM]</span></div>"""

GOOD_ROWS = [
    ["คุณตัวอย่าง หนึ่ง", "POL-DEMO-0001", "2026-01-01", "2026-12-31", "โรงพยาบาลตัวอย่าง เอ", "REQUEST_DOC", '["สำเนาใบเสร็จค่ารักษาพยาบาล","ใบรับรองแพทย์"]'],
    ["คุณตัวอย่าง สอง", "POL-DEMO-0002", "2026-02-01", "2027-01-31", "โรงพยาบาลตัวอย่าง บี", "APPROVED", "[]"],
    ["คุณตัวอย่าง สาม", "POL-DEMO-0003", "2026-03-15", "2027-03-14", "โรงพยาบาลตัวอย่าง ซี", "REQUEST_DOC", '["ผลตรวจทางห้องปฏิบัติการ"]'],
]

def fix_row(n, field, mid):
    m = MSG[mid]
    return f"<tr><td><b>แถวที่ {n}</b></td><td>{e(field)}</td><td>{e(m['message_th'])}<br><span class='muted'>{e(m['meaning_th'])}</span></td><td>{e(m['action_th'])}</td></tr>"

SCREENS = {}
SCREENS["s1-choose"] = ("เลือกชนิดเอกสาร", 0, f"""
<div class="card"><h1>เริ่มรอบงานใหม่</h1><p class="muted">เลือกชนิดเอกสารที่ต้องการสร้าง จะเห็นเฉพาะชนิดที่อนุมัติแล้วและทีมของคุณมีสิทธิ์ใช้</p>
<div class="grid"><div class="doc"><h2>ขอเอกสารเพิ่มเติมจากลูกค้า</h2><p class="muted">เวอร์ชัน 1 · เผยแพร่แล้ว</p><a class="btn" href="s2-download.html">เริ่มรอบงานใหม่</a></div>
<div class="doc off"><h2>ชนิดอื่น</h2><p>จะปรากฏที่นี่เมื่อทีมของคุณได้รับสิทธิ์</p></div></div></div>""")
SCREENS["s2-download"] = ("ดาวน์โหลดไฟล์แม่แบบ", 1, f"""
<div class="card"><h1>ดาวน์โหลดไฟล์แม่แบบ</h1><p>ใช้ไฟล์นี้ทุกครั้ง อย่าสร้างไฟล์ใหม่เอง เพราะหัวคอลัมน์ต้องตรงกับแม่แบบ</p>
<p><a class="btn" href="s3-fill.html">ดาวน์โหลดไฟล์ Excel แม่แบบ</a></p>
<ul><li>กรอกหนึ่งแถวต่อหนึ่งจดหมาย</li><li>อย่าเปลี่ยนชื่อหัวคอลัมน์ และอย่าเปลี่ยนชื่อแผ่นงาน Sheet1</li><li>ช่องสถานะให้เลือกจากรายการ</li></ul></div>""")
SCREENS["s3-fill"] = ("กรอกข้อมูลใน Excel", 2, f"""
<div class="card"><h1>กรอกข้อมูลในไฟล์ Excel</h1><p class="muted">หน้านี้คือไฟล์ Excel ที่เปิดในเครื่องของคุณ ไม่ใช่หน้าของระบบ</p>
<div style="overflow:hidden">{mock_sheet(GOOD_ROWS)}</div><p><a class="btn" href="s4-upload.html">ต่อไป: อัปโหลดไฟล์</a></p></div>""")
SCREENS["s4-upload"] = ("อัปโหลดไฟล์", 3, f"""
<div class="card"><h1>อัปโหลดไฟล์</h1><div class="drop"><h2>ลากไฟล์มาวางที่นี่ หรือกดเลือกไฟล์</h2><p>ไฟล์ที่เลือก: <b>ไฟล์ฝึกแก้ไข</b> (Excel)</p>
<a class="btn" href="s5-fix.html">ตรวจไฟล์</a></div></div>""")
SCREENS["s5-fix"] = ("ผลการตรวจ มีรายการที่ต้องแก้", 3, f"""
<div class="card"><h1>ผลการตรวจไฟล์</h1><div class="counts">
<div class="count"><b>6</b>แถวทั้งหมด</div><div class="count">{chip('READY')}<b>2</b></div><div class="count">{chip('FIX')}<b>3</b></div><div class="count">{chip('SKIP')}<b>1</b></div></div>
<p class="muted">ต้องแก้ 3 แถวก่อน จึงจะไปขั้นต่อไปได้</p></div>
<div class="card"><h2>รายการที่ต้องแก้</h2><table><tr><th>แถวที่</th><th>ช่อง</th><th>สิ่งที่พบ</th><th>วิธีแก้</th></tr>
{fix_row(4, 'ชื่อโรงพยาบาล', 'REQUIRED')}{fix_row(6, 'วันสิ้นสุดความคุ้มครอง', 'DATE_ORDER')}{fix_row(7, 'รายการเอกสาร', 'INVALID_LIST')}</table>
<p><a class="btn sec" href="s6-preview.html">ดาวน์โหลดรายการที่ต้องแก้</a> &nbsp; <a class="btn" href="s6-preview.html">อัปโหลดไฟล์ที่แก้แล้ว</a></p></div>""")
SCREENS["s6-preview"] = ("ดูตัวอย่างและขออนุมัติ", 4, f"""
<div class="card"><h1>ตรวจผ่านแล้ว ดูตัวอย่างจดหมาย</h1><div class="counts">
<div class="count"><b>5</b>แถวทั้งหมด</div><div class="count">{chip('READY')}<b>3</b></div><div class="count">{chip('FIX')}<b>0</b></div><div class="count">{chip('SKIP')}<b>2</b></div></div></div>
<div class="grid2"><div class="card"><h2>ตัวอย่างจดหมายฉบับที่ 1 จาก 3</h2>{LETTER}</div>
<div class="card"><h2>ตรวจก่อนขออนุมัติ</h2><ul><li>จำนวนจดหมายตรงกับที่คาดไหม (3 ฉบับ)</li><li>ชื่อ เลขกรมธรรม์ วันที่ ชื่อโรงพยาบาล ถูกต้องไหม</li><li>รายการเอกสารครบ เรียงเลขถูกไหม</li><li>ตัวอักษรไทยอ่านชัด ไม่มีสระหรือวรรณยุกต์ลอย</li></ul>
<p><a class="btn" href="s7-waiting.html">ขออนุมัติ</a></p></div></div>""")
SCREENS["s7-waiting"] = ("รอผู้อนุมัติ", 5, f"""
<div class="card"><h1>ส่งขออนุมัติแล้ว</h1><p>สถานะ: {chip('WAIT_APPROVAL')}</p><p class="muted">{e(MSG['WAIT_APPROVAL']['meaning_th'])}</p>
<p><a class="btn sec" href="s8-done.html">ดูหน้าเมื่ออนุมัติแล้ว</a></p></div>""")
SCREENS["s8-done"] = ("อนุมัติแล้ว ดาวน์โหลดจดหมาย", 5, f"""
<div class="card"><h1>รอบงานเสร็จแล้ว</h1><p>สถานะ: {chip('APPROVED')}</p><p class="muted">{e(MSG['APPROVED_RUN']['action_th'])}</p>
<div class="counts"><div class="count">{chip('DONE')}<b>3</b></div><div class="count">{chip('FAILED')}<b>0</b></div><div class="count">{chip('SKIP')}<b>2</b></div></div>
<p><a class="btn" href="#">ดาวน์โหลดจดหมาย</a> &nbsp; <a class="btn sec" href="#">ดาวน์โหลดรายงานสรุปรอบงาน</a></p></div>""")
SCREENS["s9-duplicate"] = ("ซ้ำกับรอบงานก่อนหน้า", 3, f"""
<div class="card"><h1>พบแถวที่ซ้ำกับรอบงานก่อนหน้า</h1><p>{chip('DUP')} &nbsp; {e(MSG['DUP_PREVIOUS_RUN']['meaning_th'])}</p>
<table><tr><th>แถวที่</th><th>เลขกรมธรรม์</th><th>รอบงานก่อนหน้า</th><th>วันที่ทำ</th></tr>
<tr><td>2</td><td>POL-DEMO-0001</td><td>รอบงานตัวอย่าง 0001</td><td>2026-10-01</td></tr>
<tr><td>4</td><td>POL-DEMO-0003</td><td>รอบงานตัวอย่าง 0001</td><td>2026-10-01</td></tr></table>
<label>เลือกวิธีจัดการ (ต้องเลือกก่อนไปต่อ)</label><div class="field">( ) ใช้ของเดิม ไม่สร้างจดหมายใหม่<br>( ) สร้างใหม่ พร้อมเขียนเหตุผลด้านล่าง</div>
<label>เหตุผล (จำเป็นถ้าเลือกสร้างใหม่)</label><div class="field" style="height:70px"></div>
<p><a class="btn" href="#">ยืนยัน</a></p></div>""")
SCREENS["s10-stop"] = ("หยุดทั้งรอบ", 3, f"""
<div class="card"><h1>ตรวจไฟล์ไม่ผ่าน</h1><p>สถานะ: {chip('STOP_FILE')}</p>
<table><tr><th>สิ่งที่พบ</th><th>หมายความว่า</th><th>วิธีแก้</th></tr><tr><td><b>{e(MSG['HEADERS_MISMATCH']['message_th'])}</b></td><td>{e(MSG['HEADERS_MISMATCH']['meaning_th'])}</td><td>{e(MSG['HEADERS_MISMATCH']['action_th'])}</td></tr></table>
<p><a class="btn" href="s4-upload.html">อัปโหลดไฟล์ใหม่</a></p></div>""")

HEIGHT = {"s5-fix": 900, "s6-preview": 1060, "s9-duplicate": 940, "s8-done": 780}
SHOTS = {  # screen -> image name used by the guide
    "s1-choose": "step1.png", "s2-download": "step2.png", "s3-fill": "step3.png", "s4-upload": "step4.png",
    "s6-preview": "step5.png", "s5-fix": "fix-list.png", "s7-waiting": "waiting.png", "s8-done": "done.png",
    "s9-duplicate": "duplicate.png", "s10-stop": "stop-file.png",
}


def main():
    OUT.mkdir(exist_ok=True)
    IMG.mkdir(parents=True, exist_ok=True)
    idx = "".join(f'<a href="{k}.html">{e(v[0])}</a>' for k, v in SCREENS.items())
    (OUT / "index.html").write_text(page("ภาพตัวอย่างหน้าจอ", -1, f'<div class="card"><h1>ภาพตัวอย่างหน้าจอทั้งหมด</h1><nav class="index">{idx}</nav></div>'), encoding="utf-8")
    for key, (title, active, body) in SCREENS.items():
        (OUT / f"{key}.html").write_text(page(title, active, body), encoding="utf-8")
    for key, img in SHOTS.items():
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size=1200,{HEIGHT.get(key, 820)}",
                        f"--screenshot={IMG / img}", (OUT / f"{key}.html").as_uri()],
                       capture_output=True, timeout=120, check=True)
        print("shot", img)

if __name__ == "__main__":
    main()
