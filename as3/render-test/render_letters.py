"""EXPERIMENT (not the platform): render 3 preview letters from validated sample rows with the
proposed HTML template + WeasyPrint. Shows (a) Thai output with the open font, (b) the proposed
transforms (strip duplicate honorific/hospital prefix, escape text, Thai date format)."""
import html
import json
import re
from datetime import datetime
from pathlib import Path

from weasyprint import HTML

here = Path(__file__).resolve().parent
root = here.parent
rows = json.loads((here / "rows_sample_request_ok.json").read_text(encoding="utf-8"))
template = (root / "templates" / "additional_document_request_v1.html").read_text(encoding="utf-8")
TH_MONTHS = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]

def strip_leading(text: str, prefix: str) -> str:
    text = text.strip()
    return text[len(prefix):].strip() if text.startswith(prefix) else text

def th_date(iso: str) -> str:               # style is [TO CONFIRM]; BE long form used for the test only
    d = datetime.fromisoformat(iso)
    return f"{d.day} {TH_MONTHS[d.month - 1]} {d.year + 543}"

out = here / "out_letters"
out.mkdir(exist_ok=True)
for row in rows[:3]:
    values = {
        "ชื่อลูกค้า": strip_leading(row["customer_name"], "คุณ"),
        "เลขกรมธรรม์": row["policy_number"],
        "วันเริ่มคุ้มครอง": th_date(row["start"]),
        "วันสิ้นสุดคุ้มครอง": th_date(row["end"]),
        "ชื่อโรงพยาบาล": strip_leading(row["hospital_name"], "โรงพยาบาล"),
    }
    page = template
    for key, value in values.items():
        page = page.replace("{{" + key + "}}", html.escape(value))
    items = "".join(f"<li>{html.escape(d)}</li>" for d in row["documents"])
    page = page.replace("{{รายการเอกสาร}}", f"<ol>{items}</ol>")
    assert not re.search(r"\{\{|\}\}", page), "unresolved field left in output"
    target = out / f"preview_row_{row['source_row']:04d}.pdf"
    HTML(string=page, base_url=str(root / "templates") + "/").write_pdf(str(target))
    print("wrote", target.name)
