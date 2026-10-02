"""Thai rendering test: HTML -> PDF with WeasyPrint and headless Chrome.

Run from this folder:
  DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib \
  uv run --with weasyprint --with pymupdf python run_thai_render_test.py

Writes PDFs, PNGs and results.json next to this file. It tests ONLY the
HTML -> PDF route. DOCX -> PDF (LibreOffice) is NOT tested here.
"""
import json, subprocess, sys, urllib.request
from pathlib import Path

import fitz  # PyMuPDF

HERE = Path(__file__).parent
OUT = HERE / "out"
FONTS = HERE / ".fonts"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SARABUN = {
    "Sarabun-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf",
    "Sarabun-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf",
}
TAHOMA = Path("/System/Library/Fonts/Supplemental/Tahoma.ttf")

# (id, label, text that must survive PDF text extraction unchanged)
CASES = [
    ("tone", "วรรณยุกต์และสระซ้อน", "ปู่ผู้ใหญ่ซึ่งน้ำก็ที่ตั้งให้ผู้ป่วยรักษาที่โรงพยาบาลเก๋ไก๋"),
    ("body", "ย่อหน้าจากจดหมาย (ไม่มีช่องว่างระหว่างคำ)",
     "จากการตรวจสอบรายละเอียดข้อมูลการเคลมจากทางโรงพยาบาลซึ่งเอาประกันภัยตามกรมธรรม์ดังกล่าวบริษัทมีความจำเป็นต้องให้ท่านส่งเอกสารเพิ่มเติม"),
    ("narrow", "คอลัมน์แคบ 5 ซม. ตัดบรรทัดกลางคำหรือไม่", "สำเนาใบเสร็จค่ารักษาพยาบาลและรายงานผลการตรวจสุขภาพจากโรงพยาบาลเอกชน"),
    ("mixed", "ไทยปนอังกฤษและตัวเลข", "Medical Report ของกรมธรรม์ POL-2026-000123 ระหว่าง 01/01/2026 ถึง 31/12/2026"),
    ("honorific", "คำนำหน้าและชื่อโรงพยาบาลยาว", "เรียน คุณสมชาย ใจดี จากโรงพยาบาลจุฬาลงกรณ์สภากาชาดไทยศูนย์การแพทย์"),
    ("list", "รายการเอกสารเรียงเลข", "1. สำเนาใบเสร็จค่ารักษาพยาบาล"),
]

def ensure_fonts():
    FONTS.mkdir(exist_ok=True)
    for name, url in SARABUN.items():
        p = FONTS / name
        if not p.exists():
            urllib.request.urlretrieve(url, p)

def build_html(family, regular, bold):
    rows = []
    for cid, label, text in CASES:
        cls = "narrow" if cid == "narrow" else ""
        extra = ' style="text-align:justify"' if cid == "body" else ""
        rows.append(f'<h3>{label}</h3><p class="t {cls}" id="{cid}"{extra}>{text}</p>')
    return f"""<!doctype html><html lang="th"><meta charset="utf-8">
<style>
@font-face {{ font-family: T; src: url('{regular.as_uri()}'); font-weight: 400; }}
@font-face {{ font-family: T; src: url('{bold.as_uri()}'); font-weight: 700; }}
@page {{ size: A4; margin: 20mm 24mm; }}
body {{ font-family: T; font-size: 12pt; line-height: 1.7; }}
h1 {{ font-size: 15pt }} h3 {{ font-size: 10pt; font-weight: 700; margin: 14pt 0 2pt; color:#444 }}
p.t {{ margin: 0 }} p.narrow {{ width: 5cm; border: 0.5pt solid #999; padding: 2pt }}
</style>
<h1>Thai test sheet - {family}</h1>{''.join(rows)}</html>"""

def run(cmd, env=None):
    return subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=120)

def check(pdf, family):
    doc = fitz.open(pdf)
    text = "\n".join(p.get_text() for p in doc)
    compact = "".join(text.split())
    res = {"pages": doc.page_count, "fonts": sorted({f[3] for p in doc for f in p.get_fonts()}), "text_ok": {}}
    for cid, _, expected in CASES:
        res["text_ok"][cid] = "".join(expected.split()) in compact
    doc[0].get_pixmap(dpi=110).save(str(pdf.with_suffix(".png")))
    return res

def main():
    OUT.mkdir(exist_ok=True)
    ensure_fonts()
    fonts = {"Sarabun": (FONTS / "Sarabun-Regular.ttf", FONTS / "Sarabun-Bold.ttf")}
    if TAHOMA.exists():
        fonts["Tahoma"] = (TAHOMA, Path("/System/Library/Fonts/Supplemental/Tahoma Bold.ttf"))
    results = {}
    for fam, (reg, bold) in fonts.items():
        html = OUT / f"thai_{fam}.html"
        html.write_text(build_html(fam, reg, bold), encoding="utf-8")
        # Engine 1: WeasyPrint
        wp = OUT / f"{fam}_weasyprint.pdf"
        r = run([sys.executable, "-m", "weasyprint", str(html), str(wp)])
        results[f"{fam}/weasyprint"] = check(wp, fam) if wp.exists() else {"error": r.stderr[-400:]}
        # Engine 2: headless Chrome
        cp = OUT / f"{fam}_chrome.pdf"
        r = run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                 f"--print-to-pdf={cp}", html.as_uri()])
        results[f"{fam}/chrome"] = check(cp, fam) if cp.exists() else {"error": r.stderr[-400:]}
    (HERE / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
