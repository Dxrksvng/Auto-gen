"""Fill the message tables in USER_GUIDE.md from docs/message-catalog.json,
then build the print-ready HTML and PDF (pandoc + headless Chrome).

Run: python3 scripts/build_guide.py
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDE = ROOT / "USER_GUIDE.md"
CAT = json.loads((ROOT / "docs" / "message-catalog.json").read_text(encoding="utf-8"))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def chips_table() -> str:
    rows = ["| ป้ายที่เห็น | หมายความว่า | ต้องทำอะไร |", "| --- | --- | --- |"]
    for c in CAT["row_chips"] + CAT["run_chips"]:
        rows.append(f"| **{cell(c['label_th'])}** | {cell(c['meaning_th'])} | {cell(c['action_th'])} |")
    return "\n".join(rows)


def messages_table() -> str:
    rows = ["| เกิดเมื่อ | ข้อความที่เห็น | หมายความว่า | ต้องทำอะไร |", "| --- | --- | --- | --- |"]
    for m in CAT["messages"]:
        rows.append(f"| {cell(m['level'])} | **{cell(m['message_th'])}** | {cell(m['meaning_th'])} | {cell(m['action_th'])} |")
    return "\n".join(rows)


def fill(text: str, name: str, body: str) -> str:
    pat = re.compile(rf"(<!-- TABLE:{name}:START -->)(.*?)(<!-- TABLE:{name}:END -->)", re.S)
    if not pat.search(text):
        raise SystemExit(f"marker {name} not found")
    return pat.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(3)}", text)


CSS = """<style>
@font-face { font-family: S; src: url('docs/rendering-test/.fonts/Sarabun-Regular.ttf'); font-weight: 400; }
@font-face { font-family: S; src: url('docs/rendering-test/.fonts/Sarabun-Bold.ttf'); font-weight: 700; }
@page { size: A4; margin: 18mm 16mm; }
body { font-family: S, Tahoma, sans-serif; font-size: 12pt; line-height: 1.6; color: #15212B; max-width: none; }
h1 { font-size: 22pt; margin: 0 0 8pt; } h2 { font-size: 16pt; margin: 18pt 0 6pt; border-bottom: 1.5pt solid #0B6E78; padding-bottom: 2pt; }
h3 { font-size: 13pt; margin: 14pt 0 4pt; } h2, h3 { break-after: avoid; }
blockquote { margin: 8pt 0; padding: 6pt 12pt; background: #FFF0D2; border-left: 4pt solid #8F5400; }
img { max-width: 100%; max-height: 9.5cm; border: 0.5pt solid #C9D1D8; display: block; margin: 6pt 0; break-inside: avoid; }
table { border-collapse: collapse; width: 100%; font-size: 10.5pt; margin: 8pt 0; }
th, td { border: 0.5pt solid #B9C2CA; padding: 4pt 6pt; vertical-align: top; text-align: left; }
th { background: #E8F3F4; } tr { break-inside: avoid; }
ul { padding-left: 16pt; } li { margin: 2pt 0; } input[type=checkbox] { margin-right: 6pt; }
header#title-block-header { display: none; }
</style>"""


def main() -> None:
    text = GUIDE.read_text(encoding="utf-8")
    text = fill(text, "CHIPS", chips_table())
    text = fill(text, "MESSAGES", messages_table())
    GUIDE.write_text(text, encoding="utf-8")
    header = ROOT / "scripts" / ".guide_header.html"
    header.write_text(CSS, encoding="utf-8")
    html_out = ROOT / "USER_GUIDE_print.html"
    subprocess.run(["pandoc", str(GUIDE), "-f", "gfm", "-t", "html5", "-s", "--metadata", "title=คู่มือผู้ใช้",
                    "--metadata", "lang=th", "-H", str(header), "-o", str(html_out)], check=True)
    pdf_out = ROOT / "USER_GUIDE.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_out}", html_out.as_uri()], capture_output=True, timeout=180, check=True)
    print("built", html_out.name, pdf_out.name)


if __name__ == "__main__":
    main()
