"""Row-level validation: required fields, dates, status, document list and names."""

import json
import re
from datetime import datetime

import pytest
from openpyxl.utils.datetime import to_excel

from validation import validate_row

THAI = re.compile(r"[฀-๿]")


def valid_row():
    return {
        "customer_name": "สมชาย ใจดี",
        "policy_number": "POL-TEST",
        "coverage_start_date": datetime(2026, 1, 1),
        "coverage_end_date": datetime(2026, 12, 31),
        "hospital_name": "กรุงเทพ",
        "claim_status": "REQUEST_DOC",
        "document_request": json.dumps(["Medical Report"], ensure_ascii=False),
    }


def codes(issues, severity=None):
    return {i.code for i in issues if severity is None or i.severity == severity}


def test_valid_request_row_has_no_issues():
    assert validate_row(2, valid_row()) == []


def test_request_requires_documents():
    row = valid_row()
    row["document_request"] = "[]"
    assert codes(validate_row(2, row)) == {"REQUIRED_FOR_REQUEST"}


def test_invalid_date_order_and_unknown_status_are_reported():
    row = valid_row()
    row["coverage_start_date"] = datetime(2027, 1, 1)
    row["claim_status"] = "NEW_STATUS"
    assert codes(validate_row(2, row)) == {"DATE_ORDER", "UNKNOWN_STATUS"}


def test_end_before_start_has_a_clear_code_and_thai_message():
    row = valid_row()
    row["coverage_end_date"] = datetime(2025, 12, 31)
    (issue,) = validate_row(5, row)
    found = (issue.code, issue.field, issue.source_row, issue.severity)
    assert found == ("DATE_ORDER", "coverage_end_date", 5, "error")
    assert "วันสิ้นสุด" in issue.message


@pytest.mark.parametrize(
    "value",
    ["2026-01-01", "01/01/2026", to_excel(datetime(2026, 1, 1)), "46023"],
)
def test_start_date_accepts_strings_and_excel_serials(value):
    row = valid_row()
    row["coverage_start_date"] = value
    assert validate_row(2, row) == []


def test_unreadable_date_is_reported_not_raised():
    row = valid_row()
    row["coverage_start_date"] = "not a date"
    (issue,) = validate_row(2, row)
    assert issue.code == "INVALID_DATE"
    assert issue.field == "coverage_start_date"


def test_unknown_document_name_is_an_error_naming_the_document():
    row = valid_row()
    row["document_request"] = json.dumps(["Discharge Summary", "ใบรับรองแพทย์"])
    (issue,) = validate_row(2, row)
    assert issue.code == "UNKNOWN_DOCUMENT"
    assert "Discharge Summary" in issue.message
    assert THAI.search(issue.message)
    assert issue.severity == "error"


def test_unknown_document_is_ignored_for_rows_that_will_not_print_it():
    row = valid_row()
    row["claim_status"] = "APPROVED"
    row["document_request"] = json.dumps(["Discharge Summary"])
    assert "UNKNOWN_DOCUMENT" not in codes(validate_row(2, row))


def test_unrecognized_name_format_is_only_a_warning():
    row = valid_row()
    row["customer_name"] = "สมชาย 123"
    (issue,) = validate_row(2, row)
    assert (issue.code, issue.severity) == ("NAME_FORMAT", "warning")


def test_blank_required_fields_are_reported_per_field():
    row = valid_row()
    row["hospital_name"] = "   "
    row["policy_number"] = None
    found = {(i.code, i.field) for i in validate_row(2, row)}
    assert found == {("REQUIRED", "hospital_name"), ("REQUIRED", "policy_number")}


def test_invalid_list_text_is_reported():
    row = valid_row()
    row["document_request"] = "ใบรับรองแพทย์"
    assert codes(validate_row(2, row)) == {"INVALID_LIST"}


def test_every_issue_message_is_thai():
    bad = valid_row()
    bad.update(
        customer_name="x 1", hospital_name="", claim_status="???", document_request="oops",
        coverage_start_date="zzz", coverage_end_date=datetime(2020, 1, 1),
    )  # fmt: skip
    issues = validate_row(2, bad)
    assert len(issues) >= 4
    assert all(THAI.search(i.message) for i in issues), [i for i in issues if not THAI.search(i.message)]
