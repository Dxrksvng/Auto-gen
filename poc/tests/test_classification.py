"""Workbook-level classification: generate / skip / conflict / duplicate / reject."""

import json
from datetime import datetime
from pathlib import Path

import pytest
from conftest import make_xlsx

from validation import FileValidationError, load_and_validate

SAMPLE = Path(__file__).resolve().parents[2] / "data" / "Example claim table.xlsx"
D1, D2 = datetime(2026, 1, 1), datetime(2026, 12, 31)


def row(name="สมชาย ใจดี", policy="P1", status="REQUEST_DOC", docs=("ใบรับรองแพทย์",), hospital="กรุงเทพ"):
    return [name, policy, D1, D2, hospital, status, json.dumps(list(docs), ensure_ascii=False)]


def codes(result, severity=None):
    return [i.code for i in result.issues if severity is None or i.severity == severity]


def test_sample_workbook_reconciles_and_normalizes_values():
    result = load_and_validate(SAMPLE)
    counts = result.counts()
    assert counts == {"populated": 10, "eligible": 5, "rejected": 0, "skipped": 5, "conflicts": 0, "duplicates": 0}
    first = result.letters[0]
    assert first.source_row == 2
    assert first.salutation == "คุณสมชาย ใจดี"
    assert first.hospital == "โรงพยาบาลกรุงเทพ"
    assert (first.coverage_start_date.year, first.coverage_end_date.year) == (2026, 2026)
    by_row = {letter.source_row: letter for letter in result.letters}
    assert "รายงานทางการแพทย์" in by_row[4].requested_documents
    assert "Medical Report" not in by_row[4].requested_documents


def test_status_other_than_request_with_documents_is_a_listed_conflict(tmp_path):
    path = make_xlsx(tmp_path / "c.xlsx", [row(status="APPROVED", docs=("ใบรับรองแพทย์",))])
    result = load_and_validate(path)
    assert result.letters == []
    assert result.counts()["skipped"] == 1
    assert result.counts()["conflicts"] == 1
    (issue,) = [i for i in result.issues if i.code == "CONFLICTING_ROW"]
    assert "ข้อมูลขัดแย้ง ตรวจสอบ" in issue.message
    assert issue.source_row == 2


def test_status_other_than_request_without_documents_is_a_plain_skip(tmp_path):
    path = make_xlsx(tmp_path / "s.xlsx", [row(status="REJECTED", docs=())])
    result = load_and_validate(path)
    assert result.counts()["skipped"] == 1
    assert result.counts()["conflicts"] == 0
    assert "CONFLICTING_ROW" not in codes(result)


def test_duplicate_policy_and_documents_generates_one_and_reports_both_rows(tmp_path):
    path = make_xlsx(tmp_path / "d.xlsx", [row(), row()])
    result = load_and_validate(path)
    assert [letter.source_row for letter in result.letters] == [2]
    assert result.counts()["duplicates"] == 1
    messages = " ".join(i.message for i in result.issues if i.code == "DUPLICATE_ROW")
    assert "2" in messages
    assert "3" in messages


def test_duplicate_detection_ignores_document_order(tmp_path):
    docs = ("ใบรับรองแพทย์", "Medical Report")
    path = make_xlsx(tmp_path / "d2.xlsx", [row(docs=docs), row(docs=tuple(reversed(docs)))])
    assert load_and_validate(path).counts()["duplicates"] == 1


def test_same_policy_with_different_documents_is_not_a_duplicate(tmp_path):
    path = make_xlsx(tmp_path / "n.xlsx", [row(docs=("ใบรับรองแพทย์",)), row(docs=("Medical Report",))])
    result = load_and_validate(path)
    assert len(result.letters) == 2
    assert result.counts()["duplicates"] == 0


def test_unknown_document_rejects_the_row(tmp_path):
    path = make_xlsx(tmp_path / "u.xlsx", [row(docs=("Discharge Summary",)), row(policy="P2")])
    result = load_and_validate(path)
    assert [letter.policy_number for letter in result.letters] == ["P2"]
    assert result.rejected_rows == {2}
    assert "UNKNOWN_DOCUMENT" in codes(result, "error")


def test_excel_serial_number_dates_are_converted(tmp_path):
    from openpyxl.utils.datetime import to_excel

    values = row()
    values[2], values[3] = to_excel(D1), to_excel(D2)
    result = load_and_validate(make_xlsx(tmp_path / "e.xlsx", [values]))
    assert result.counts()["eligible"] == 1
    assert result.letters[0].coverage_start_date.isoformat() == "2026-01-01"


def test_numeric_policy_number_is_read_as_text(tmp_path):
    values = row()
    values[1] = 12345.0
    result = load_and_validate(make_xlsx(tmp_path / "p.xlsx", [values]))
    assert result.letters[0].policy_number == "12345"


def test_counts_always_reconcile(tmp_path):
    rows = [
        row(), row(),  # duplicate
        row(policy="P3", status="APPROVED", docs=()),  # skipped
        row(policy="P4", status="APPROVED", docs=("ใบรับรองแพทย์",)),  # conflict (skipped)
        row(policy="P5", docs=("Discharge Summary",)),  # rejected
        row(policy="P6", hospital=""),  # rejected
        row(policy="P7", docs=("Medical Report",)),  # eligible
    ]  # fmt: skip
    c = load_and_validate(make_xlsx(tmp_path / "r.xlsx", rows)).counts()
    assert c["populated"] == 7
    assert c["populated"] == c["rejected"] + c["skipped"] + c["duplicates"] + c["eligible"]


def test_empty_rows_are_not_counted(tmp_path):
    path = make_xlsx(tmp_path / "b.xlsx", [row(), [None] * 7, row(policy="P2")])
    assert load_and_validate(path).counts()["populated"] == 2


@pytest.mark.parametrize(
    ("kwargs", "code"),
    [({"headers": ["a", "b"]}, "HEADERS_MISMATCH"), ({"sheet_title": "Other"}, "SHEET_MISSING")],
)
def test_file_level_problems_raise_with_a_code(tmp_path, kwargs, code):
    path = make_xlsx(tmp_path / "f.xlsx", [row()], **kwargs)
    with pytest.raises(FileValidationError) as info:
        load_and_validate(path)
    assert info.value.code == code


def test_unreadable_file_raises_with_a_code(tmp_path):
    bad = tmp_path / "bad.xlsx"
    bad.write_bytes(b"not an excel file")
    with pytest.raises(FileValidationError) as info:
        load_and_validate(bad)
    assert info.value.code == "FILE_UNREADABLE"


# --- architect review: a "duplicate" must be identical in everything the letter prints ---


@pytest.mark.parametrize(
    ("second", "differs"),
    [
        (row(hospital="สมิติเวช"), "hospital_name"),
        (row(name="สมหญิง ใจดี"), "customer_name"),
    ],
)
def test_same_policy_and_documents_but_different_letter_content_is_not_suppressed(tmp_path, second, differs):
    path = make_xlsx(tmp_path / "s.xlsx", [row(), second])
    result = load_and_validate(path)
    assert [letter.source_row for letter in result.letters] == [2, 3]  # two different letters, none lost
    assert result.counts()["duplicates"] == 0
    similar = [i for i in result.issues if i.code == "SIMILAR_ROW"]
    assert [(i.source_row, i.severity) for i in similar] == [(3, "warning")]
    assert differs in similar[0].message


def test_same_policy_and_documents_but_different_dates_is_not_suppressed(tmp_path):
    other = row()
    other[2], other[3] = datetime(2027, 1, 1), datetime(2027, 12, 31)
    result = load_and_validate(make_xlsx(tmp_path / "s2.xlsx", [row(), other]))
    assert len(result.letters) == 2
    assert [i.source_row for i in result.issues if i.code == "SIMILAR_ROW"] == [3]
    assert "coverage" in next(i.message for i in result.issues if i.code == "SIMILAR_ROW")


def test_identical_rows_are_still_one_letter_and_not_reported_as_similar(tmp_path):
    result = load_and_validate(make_xlsx(tmp_path / "s3.xlsx", [row(), row()]))
    assert len(result.letters) == 1
    assert result.counts()["duplicates"] == 1
    assert "SIMILAR_ROW" not in codes(result)


def test_headers_mismatch_names_the_missing_and_unexpected_columns(tmp_path):
    from validation import HEADERS

    headers = [h for h in HEADERS if h != "hospital_name"] + ["hospital"]
    with pytest.raises(FileValidationError) as info:
        load_and_validate(make_xlsx(tmp_path / "h.xlsx", [row()], headers=headers))
    assert info.value.code == "HEADERS_MISMATCH"
    message = info.value.message
    assert "ขาดคอลัมน์: hospital_name" in message
    assert "คอลัมน์ที่ไม่รู้จัก" in message and "hospital" in message.split("คอลัมน์ที่ไม่รู้จัก")[1]


def test_headers_mismatch_reports_wrong_order_when_nothing_is_missing(tmp_path):
    from validation import HEADERS

    swapped = list(HEADERS)
    swapped[0], swapped[1] = swapped[1], swapped[0]
    with pytest.raises(FileValidationError) as info:
        load_and_validate(make_xlsx(tmp_path / "o.xlsx", [row()], headers=swapped))
    assert info.value.code == "HEADERS_MISMATCH"
    assert "ลำดับคอลัมน์ไม่ตรง" in info.value.message
    assert "ขาดคอลัมน์" not in info.value.message
