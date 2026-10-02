import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from validation import validate_row


def valid_row():
    return {
        "customer_name": "Test Customer",
        "policy_number": "POL-TEST",
        "coverage_start_date": datetime(2026, 1, 1),
        "coverage_end_date": datetime(2026, 12, 31),
        "hospital_name": "Test Hospital",
        "claim_status": "REQUEST_DOC",
        "document_request": json.dumps(["Medical Report"]),
    }


def test_valid_request_row_has_no_issues():
    assert validate_row(2, valid_row()) == []


def test_request_requires_documents():
    row = valid_row()
    row["document_request"] = "[]"
    assert {issue.code for issue in validate_row(2, row)} == {"REQUIRED_FOR_REQUEST"}


def test_invalid_date_order_and_unknown_status_are_reported():
    row = valid_row()
    row["coverage_start_date"] = datetime(2027, 1, 1)
    row["claim_status"] = "NEW_STATUS"
    assert {issue.code for issue in validate_row(2, row)} == {"DATE_ORDER", "UNKNOWN_STATUS"}

