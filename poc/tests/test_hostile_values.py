"""Values typed into Excel are data, never markup or template instructions."""

import json
from datetime import datetime

import pytest
from conftest import make_xlsx

from generate_letters import run

D1, D2 = datetime(2026, 1, 1), datetime(2026, 12, 31)

HOSTILE = {
    "html_tags": ("<script>alert(1)</script> <b>x</b>", "โรงพยาบาล<img src=x>"),
    "entities_and_quotes": ("A & B \"quoted\" &amp; 'single'", "โรงพยาบาล &lt;ทดสอบ&gt;"),
    "template_slot_names": ("{{CLOSING}} {{ITEMS}}", "{{LOGO}}{{BANNER}}"),
    "emoji_and_thai_digits": ("สมชาย 😀 ๑๒๓", "โรงพยาบาลเอ 🏥"),
    "very_long_name": ("ก" * 120 + " " + "ข" * 120, "โรงพยาบาล" + "ค" * 150),
}


@pytest.mark.parametrize("case", sorted(HOSTILE))
def test_hostile_values_print_literally_and_pass_verification(tmp_path, case):
    name, hospital = HOSTILE[case]
    docs = json.dumps(["ใบรับรองแพทย์"], ensure_ascii=False)
    workbook = make_xlsx(tmp_path / "h.xlsx", [[name, "P-1", D1, D2, hospital, "REQUEST_DOC", docs]])
    run_dir = run(workbook, tmp_path / "out")
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["counts"]["generated"] == 1, manifest["failed"]
    assert manifest["counts"]["failed"] == 0
