"""Build final/submission/Assignment_2_to_4.pdf from as2/ANSWER.md, as3/ANSWER.md, as4/ANSWER.md.

Content is NOT edited. Formatting-only changes: Mermaid blocks -> PNG, relative links -> plain text,
task-list boxes -> drawn boxes, headings get ids. Run with the Python that has weasyprint + markdown + PIL
(python 3.11 from pyenv in this project):   python3 tools/build_submission.py
Chrome is used only to rasterize Mermaid (macOS path below).
"""
import html
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import markdown
from PIL import Image, ImageChops
from weasyprint import HTML

SUNDAY = Path(__file__).resolve().parents[2]
AS3 = SUNDAY / "as3"
FONTS = AS3 / "assets" / "fonts"
MERMAID_JS = AS3 / "assets" / "vendor" / "mermaid.min.js"
OUT_DIR = SUNDAY / "final" / "submission"
DIAGRAM_DIR = SUNDAY / "final" / "diagrams"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SOURCES = [("A2", SUNDAY / "as2" / "ANSWER.md"), ("A3", SUNDAY / "as3" / "ANSWER.md"), ("A4", SUNDAY / "as4" / "ANSWER.md")]
CANDIDATE_NAME = "Nattakamon Jaimetha"
DOC_DATE = "2 ตุลาคม 2569 (2 October 2026)"

MERMAID_PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:SarabunT;src:url('{font_uri}/Sarabun-Regular.ttf');font-weight:400}}
@font-face{{font-family:SarabunT;src:url('{font_uri}/Sarabun-Bold.ttf');font-weight:700}}
body{{margin:0;padding:16px;background:#fff;font-family:SarabunT}}</style></head><body>
<pre class="mermaid">
{src}
</pre><script src="{js_uri}"></script><script>
mermaid.initialize({{startOnLoad:true,theme:'base',securityLevel:'strict',
 themeVariables:{{fontFamily:'SarabunT',fontSize:'18px',primaryColor:'#eaf0ff',primaryBorderColor:'#1a56db',primaryTextColor:'#1d2433',lineColor:'#41507a'}},
 flowchart:{{htmlLabels:true,useMaxWidth:false,curve:'basis',nodeSpacing:24,rankSpacing:30,padding:10,wrappingWidth:420}},
 er:{{useMaxWidth:false}}}});
</script></body></html>"""


def render_mermaid(src: str, png: Path) -> None:
    png.parent.mkdir(parents=True, exist_ok=True)
    page = png.with_suffix(".tmp.html")
    page.write_text(MERMAID_PAGE.format(src=html.escape(src, quote=False), font_uri=FONTS.as_uri(), js_uri=MERMAID_JS.as_uri()), encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                    "--window-size=3600,4200", "--virtual-time-budget=10000", f"--screenshot={png}", page.as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    page.unlink()
    img = Image.open(png).convert("RGB")
    box = ImageChops.difference(img, Image.new("RGB", img.size, (255, 255, 255))).getbbox()
    pad = 24
    img.crop((max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, img.width), min(box[3] + pad, img.height))).save(png)


def preprocess(md: str, tag: str, src_dir: Path) -> str:
    """Formatting-only fixes on the Markdown text."""
    counter = 0

    def mermaid_sub(m):
        nonlocal counter
        counter += 1
        png = DIAGRAM_DIR / f"{tag.lower()}_diagram_{counter}.png"
        src = m.group(1)
        render_mermaid(src, png)
        w, h = Image.open(png).size
        if w / h > 2.2 and re.search(r"flowchart\s+LR", src):   # too wide to read on A4 -> lay out top-down
            render_mermaid(re.sub(r"flowchart\s+LR", "flowchart TD", src, count=1), png)
        return f"\n\n![diagram {tag}-{counter}]({png.as_uri()})\n\n"

    md = re.sub(r"```mermaid\n(.*?)```", mermaid_sub, md, flags=re.S)
    # relative file links (not images, not http) -> plain text; they cannot work inside a PDF
    md = re.sub(r"(?<!!)\[([^\]]+)\]\((?!https?://|#|file:)[^)]*\)", r"\1", md)
    # relative image paths -> absolute file URIs (only used while building; not stored in the PDF)
    def img_sub(m):
        alt, target = m.group(1), m.group(2)
        if re.match(r"(https?|file):", target):
            return m.group(0)
        return f"![{alt}]({(src_dir / target).resolve().as_uri()})"
    md = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", img_sub, md)
    md = re.sub(r"^(\s*)- \[ \] ", r'\1- <span class="cb"></span>', md, flags=re.M)
    md = re.sub(r"^(\s*)- \[[xX]\] ", r'\1- <span class="cb on"></span>', md, flags=re.M)
    return md


def to_html(md: str) -> str:
    out = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists", "md_in_html"], output_format="html5")
    # a paragraph that introduces a table stays with it; tables longer than 7 rows may break between rows
    out = re.sub(r"<p>((?:(?!</p>).)*)</p>(\s*)<table>", r'<p class="keep">\1</p>\2<table>', out, flags=re.S)
    def mark_big(m):
        return '<table class="big">' if m.group(0).count("<tr") > 8 else "<table>"
    out = re.sub(r"<table>(?:(?!</table>).)*", lambda m: mark_big(m) + m.group(0)[len("<table>"):], out, flags=re.S)
    return out


CSS = """
@font-face{font-family:SarabunT;src:url('%(f)s/Sarabun-Regular.ttf');font-weight:400;font-style:normal}
@font-face{font-family:SarabunT;src:url('%(f)s/Sarabun-Bold.ttf');font-weight:700;font-style:normal}
@font-face{font-family:SarabunT;src:url('%(f)s/Sarabun-Italic.ttf');font-weight:400;font-style:italic}
@font-face{font-family:SarabunT;src:url('%(f)s/Sarabun-BoldItalic.ttf');font-weight:700;font-style:italic}
@font-face{font-family:MonoT;src:url('%(f)s/DejaVuSansMono.ttf');font-weight:400}
@font-face{font-family:MonoT;src:url('%(f)s/DejaVuSansMono-Bold.ttf');font-weight:700}
@font-face{font-family:SymT;src:url('%(f)s/DejaVuSans.ttf')}
@page{size:A4;margin:18mm 17mm 20mm 17mm;
  @bottom-left{content:"Strictly Confidential";font:8pt SarabunT;color:#666}
  @bottom-center{content:"%(name)s";font:8pt SarabunT;color:#666}
  @bottom-right{content:counter(page) " / " counter(pages);font:8pt SarabunT;color:#666}}
@page:first{@bottom-left{content:none}@bottom-center{content:none}@bottom-right{content:none}}
html{font-family:SarabunT,SymT,sans-serif;font-size:10.5pt;line-height:1.5;color:#1d2433}
h1{font-size:20pt;margin:0 0 5mm;padding-bottom:2mm;border-bottom:0.6mm solid #1a56db;break-before:page;break-after:avoid}
h1.first{break-before:auto}
h2{font-size:14pt;margin:7mm 0 2.5mm;color:#12306b;break-after:avoid}
h3{font-size:12pt;margin:5mm 0 2mm;break-after:avoid}
h4,h5{font-size:11pt;margin:4mm 0 1.5mm;break-after:avoid}
p{margin:0 0 2.6mm;orphans:3;widows:3}
p.keep{break-after:avoid}
table.big{break-inside:auto}
a{color:#1a56db;text-decoration:none}
ul,ol{margin:0 0 3mm;padding-left:6mm}li{margin-bottom:1mm}
blockquote{margin:3mm 0;padding:2mm 4mm;border-left:1mm solid #d98200;background:#fff7e6;break-inside:avoid}
blockquote p{margin:0 0 1.5mm}
table{border-collapse:collapse;width:100%%;font-size:9pt;margin:3mm 0 4mm;break-inside:avoid-page}
th,td{border:0.2mm solid #b8c0cc;padding:1.2mm 1.8mm;vertical-align:top;overflow-wrap:anywhere}
th{background:#eaeff8;text-align:left}thead{display:table-header-group}tr{break-inside:avoid}
code{font-family:MonoT,SarabunT,monospace;font-size:8.6pt;background:#f1f3f7;padding:0 0.6mm;overflow-wrap:anywhere}
pre{font-family:MonoT,SarabunT,monospace;font-size:7.6pt;line-height:1.35;background:#f6f7fa;border:0.2mm solid #d5dae3;padding:2.5mm;white-space:pre-wrap;overflow-wrap:anywhere;margin:2mm 0 4mm}
pre code{background:none;padding:0;font-size:inherit}
img{display:block;margin:3mm auto;max-width:100%%;max-height:215mm;break-inside:avoid}
.cb{display:inline-block;width:3.2mm;height:3.2mm;border:0.35mm solid #1d2433;margin-right:2mm;vertical-align:-0.4mm}
.cb.on{background:#1d2433}
li:has(> .cb){list-style:none;margin-left:-5mm}
.title{height:240mm;display:flex;flex-direction:column;justify-content:center}
.title .conf{display:inline-block;border:0.5mm solid #b00020;color:#b00020;font-weight:700;padding:2mm 6mm;font-size:13pt;margin-bottom:12mm;align-self:flex-start}
.title h1{border:none;font-size:27pt;line-height:1.25;break-before:auto;margin-bottom:8mm}
.title .meta{font-size:12pt;line-height:1.9}
.title .note{margin-top:14mm;font-size:9.5pt;color:#555;max-width:140mm}
.toc{list-style:none;padding:0;margin:0}
.toc li{margin:0;padding:0}
.toc a::after{content:leader('.') target-counter(attr(href url),page)}
.toc a{display:block;color:#1d2433}
.toc .l1{font-weight:700;margin-top:3.5mm;font-size:11.5pt}
.toc .l2{padding-left:7mm;font-size:10.5pt}
.confirm h2{margin-top:6mm}
.confirm li{margin-bottom:1.2mm}
"""


def collect_confirms(sections: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Return (section heading, marker text) for every [TO CONFIRM...] marker in the body text."""
    found, seen = [], set()
    for heading, body_html in sections:
        text = re.sub(r"<[^>]+>", "", body_html)
        text = html.unescape(text)
        for m in re.finditer(r"\[TO CONFIRM[^\]]*\]", text):
            ctx = text[max(0, m.start() - 70):m.start()].replace("\n", " ").strip()
            key = (heading, m.group(0), ctx[-40:])
            if key not in seen:
                seen.add(key)
                found.append((heading, f"{ctx} {m.group(0)}".strip()))
    return found


def build() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    body_parts, toc, sections, idn = [], [], [], 0

    def add_ids(doc_html: str, first: bool) -> str:
        nonlocal idn
        def sub(m):
            nonlocal idn
            idn += 1
            level, inner = m.group(1), m.group(2)
            hid = f"h{idn}"
            toc.append((int(level), hid, re.sub(r"<[^>]+>", "", html.unescape(inner))))
            cls = ' class="first"' if (level == "1" and first and not body_parts) else ""
            return f'<h{level} id="{hid}"{cls}>{inner}</h{level}>'
        return re.sub(r"<h([12])>(.*?)</h\1>", sub, doc_html, flags=re.S)

    for tag, path in SOURCES:
        md = path.read_text(encoding="utf-8")
        h = add_ids(to_html(preprocess(md, tag, path.parent)), first=False)
        body_parts.append(h)
        # split by H2 for the TO CONFIRM listing
        for chunk in re.split(r"(?=<h[12] id=)", h):
            mh = re.match(r'<h[12] id="[^"]+"[^>]*>(.*?)</h[12]>', chunk, flags=re.S)
            sections.append((re.sub(r"<[^>]+>", "", html.unescape(mh.group(1))) if mh else tag, chunk))
    confirms = collect_confirms(sections)

    toc_html = '<h1 id="toc" class="toc-h">สารบัญ / Contents</h1><ul class="toc">' + "".join(
        f'<li class="l{lv}"><a href="#{hid}">{html.escape(txt)}</a></li>' for lv, hid, txt in toc) + "</ul>"
    if confirms:
        items, cur = [], None
        for sec, txt in confirms:
            if sec != cur:
                items.append(f"</ul><h2>{html.escape(sec)}</h2><ul>" if cur else f"<h2>{html.escape(sec)}</h2><ul>")
                cur = sec
            items.append(f"<li>{html.escape(txt)}</li>")
        confirm_html = ('<h1 id="confirm">สิ่งที่ต้องยืนยัน</h1><div class="confirm"><p>รายการนี้รวบรวมอัตโนมัติจากทุกจุดที่เขียนว่า '
                        f'<b>[TO CONFIRM]</b> ในเอกสารนี้ (รวม {len(confirms)} จุด) แต่ละข้อเป็นข้อเท็จจริงขององค์กรที่ผู้เขียนไม่ทราบ และไม่ได้สมมติขึ้นเอง</p>'
                        + "".join(items) + "</ul></div>")
    else:
        confirm_html = '<h1 id="confirm">สิ่งที่ต้องยืนยัน</h1><p>ไม่มีรายการ [TO CONFIRM] ค้างอยู่ในเอกสารนี้</p>'
    title_html = f"""<div class="title"><div class="conf">Strictly Confidential</div>
<h1>Forward Deployed AI Engineer Assignment — Answers 2–4</h1>
<div class="meta"><b>Candidate:</b> {CANDIDATE_NAME}<br><b>Date:</b> {DOC_DATE}<br><b>Source:</b> Sunday, Forward Deployed AI-Eng 2026 Assignment, pp. 7, 9, 11<br>
<b>Contents:</b> Assignment 2 (2.1–2.3) · Assignment 3 (3.1–3.4) · Assignment 4 (4.1–4.5)</div>
<div class="note">เอกสารลับ — ใช้เพื่อการพิจารณางานนี้เท่านั้น ห้ามเผยแพร่ ข้อเสนอในเอกสารนี้ไม่ใช่ระบบที่ทำงานอยู่จริง ยกเว้นส่วนที่ระบุชัดว่าเป็นของที่มีอยู่และตรวจแล้ว</div></div>"""
    doc = f"<!doctype html><html lang='th'><head><meta charset='utf-8'><title>Assignment 2-4 — {CANDIDATE_NAME}</title><style>{CSS % {'f': FONTS.as_uri(), 'name': CANDIDATE_NAME}}</style></head><body>{title_html}{toc_html}{''.join(body_parts)}{confirm_html}</body></html>"
    html_path = OUT_DIR / "_build.html"
    html_path.write_text(doc, encoding="utf-8")
    out = OUT_DIR / "Assignment_2_to_4.pdf"
    HTML(string=doc).write_pdf(str(out))
    html_path.unlink()
    print("wrote", out, f"({out.stat().st_size/1024:.0f} KB); TO CONFIRM markers listed: {len(confirms)}")
    return out


if __name__ == "__main__":
    build()
