"""Fill the message tables in USER_GUIDE.src.md from definitions/messages_th.yaml -> USER_GUIDE.md.

The tables are generated so that every message code defined in the YAML appears in the guide.
Usage: python3 tools/build_guide.py
"""
from pathlib import Path

import yaml

root = Path(__file__).resolve().parent.parent
msgs = yaml.safe_load((root / "definitions" / "messages_th.yaml").read_text(encoding="utf-8"))
src = (root / "USER_GUIDE.src.md").read_text(encoding="utf-8")


def table(rows, with_status=False):
    head = "| ข้อความที่เห็น | ความหมาย | วิธีแก้ |\n|---|---|---|\n"
    lines = []
    for r in rows:
        shown = r.get("shown_th", r["meaning_th"])
        if with_status and r.get("status_th"):
            shown = f"**{r['status_th']}**: {shown}"
        lines.append(f"| {shown} | {r['meaning_th']} | {r['fix_th']} |")
    return head + "\n".join(lines)


out = (src.replace("{{ตารางแถว}}", table(msgs["row_messages"], with_status=True))
          .replace("{{ตารางไฟล์}}", table(msgs["file_messages"]))
          .replace("{{ตารางสร้าง}}", table(msgs["generation_messages"])))
(root / "USER_GUIDE.md").write_text(out, encoding="utf-8")
print("wrote USER_GUIDE.md", len(out), "chars")
