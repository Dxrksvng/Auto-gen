import json
import sys
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook

sys.path.insert(0, str(Path(__file__).parents[1]))

from generate_letters import run
from validation import HEADERS


def test_sample_batch_is_reconciled(tmp_path):
    source = Path(__file__).parents[2] / "data" / "Example claim table.xlsx"
    batch_dir = run(source, tmp_path)
    manifest = json.loads((batch_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["counts"] == {
        "populated": 10,
        "eligible": 5,
        "rejected": 0,
        "skipped": 5,
        "generated": 5,
        "failed": 0,
    }
    assert len(list((batch_dir / "letters").glob("*.pdf"))) == 5


def test_rerun_uses_same_batch_and_output_names(tmp_path):
    source = Path(__file__).parents[2] / "data" / "Example claim table.xlsx"
    first = run(source, tmp_path)
    first_names = sorted(path.name for path in (first / "letters").glob("*.pdf"))
    second = run(source, tmp_path)
    second_names = sorted(path.name for path in (second / "letters").glob("*.pdf"))
    assert first == second
    assert first_names == second_names


def test_invalid_row_is_rejected_with_actionable_error(tmp_path):
    source = tmp_path / "invalid.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Sheet1"
    sheet.append(HEADERS)
    sheet.append(["Test", "POL-X", datetime(2026, 1, 1), datetime(2026, 12, 31), "Hospital", "REQUEST_DOC", "[]"])
    workbook.save(source)

    batch_dir = run(source, tmp_path / "output")
    manifest = json.loads((batch_dir / "manifest.json").read_text(encoding="utf-8"))
    rejected = (batch_dir / "rejected.csv").read_text(encoding="utf-8-sig")
    assert manifest["counts"]["rejected"] == 1
    assert manifest["counts"]["generated"] == 0
    assert "REQUIRED_FOR_REQUEST" in rejected
