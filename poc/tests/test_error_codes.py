"""Every error code the validator can emit has a fixture row that produces it.

If someone adds a code to validation.py without adding a fixture here, test_every_code_has_a_fixture fails.
"""

import ast
import json
from datetime import datetime
from pathlib import Path

import pytest
from conftest import make_xlsx
from openpyxl import Workbook

from validation import FileValidationError, load_and_validate

D1, D2 = datetime(2026, 1, 1), datetime(2026, 12, 31)


def row(
    name="สมชาย ใจดี", policy="P1", start=D1, end=D2, hospital="กรุงเทพ", status="REQUEST_DOC", docs=("ใบรับรองแพทย์",)
):
    cell = docs if isinstance(docs, str) else json.dumps(list(docs), ensure_ascii=False)
    return [name, policy, start, end, hospital, status, cell]


# code -> rows that must make the validator emit it (row-level codes)
ROW_FIXTURES = {
    "REQUIRED": [row(name="")],
    "INVALID_DATE": [row(start="not a date")],
    "DATE_ORDER": [row(start=D2, end=D1)],
    "UNKNOWN_STATUS": [row(status="PENDING")],
    "INVALID_LIST": [row(docs="not a list")],
    "REQUIRED_FOR_REQUEST": [row(docs=())],
    "UNKNOWN_DOCUMENT": [row(docs=("Discharge Summary",))],
    "NAME_FORMAT": [row(name="สมชาย123 #")],
    "CONFLICTING_ROW": [row(status="APPROVED", docs=("ใบรับรองแพทย์",))],
    "DUPLICATE_ROW": [row(), row()],
    "SIMILAR_ROW": [row(), row(hospital="สมิติเวช")],
}


@pytest.mark.parametrize("code", sorted(ROW_FIXTURES))
def test_row_fixture_produces_its_code(tmp_path, code):
    result = load_and_validate(make_xlsx(tmp_path / "f.xlsx", ROW_FIXTURES[code]))
    assert code in {i.code for i in result.issues}


def _empty_sheet(path):
    workbook = Workbook()
    workbook.active.title = "Sheet1"
    workbook.save(path)
    return path


def _not_excel(path):
    path.write_bytes(b"not an excel file")
    return path


FILE_FIXTURES = {
    "FILE_UNREADABLE": _not_excel,
    "SHEET_MISSING": lambda path: make_xlsx(path, [row()], sheet_title="Other"),
    "FILE_EMPTY": _empty_sheet,
    "HEADERS_MISMATCH": lambda path: make_xlsx(path, [row()], headers=["a", "b"]),
}


@pytest.mark.parametrize("code", sorted(FILE_FIXTURES))
def test_file_fixture_raises_its_code(tmp_path, code):
    with pytest.raises(FileValidationError) as info:
        load_and_validate(FILE_FIXTURES[code](tmp_path / "f.xlsx"))
    assert info.value.code == code


def _codes_in_source() -> set[str]:
    """Codes passed to add(...), RowIssue(...) and FileValidationError(...) in validation.py."""
    tree = ast.parse((Path(__file__).resolve().parents[1] / "validation.py").read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = getattr(node.func, "id", getattr(node.func, "attr", ""))
        index = {"add": 1, "RowIssue": 2, "FileValidationError": 0}.get(name)
        if index is not None and len(node.args) > index and isinstance(node.args[index], ast.Constant):
            found.add(node.args[index].value)
    return found


def test_every_code_has_a_fixture():
    assert _codes_in_source() == set(ROW_FIXTURES) | set(FILE_FIXTURES)
