"""A3: Thai Buddhist-era dates and robust parsing of Excel date inputs."""

from datetime import date, datetime

import pytest
from openpyxl.utils.datetime import to_excel

from normalize import DateError, parse_date, th_date


def test_th_date_uses_buddhist_year_and_thai_month():
    assert th_date(date(2026, 1, 1)) == "1 มกราคม 2569"
    assert th_date(date(2027, 12, 31)) == "31 ธันวาคม 2570"


def test_th_date_accepts_datetime_and_has_no_leading_zero():
    assert th_date(datetime(2026, 3, 5, 0, 0)) == "5 มีนาคม 2569"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (datetime(2026, 1, 31, 0, 0), date(2026, 1, 31)),
        (date(2026, 1, 31), date(2026, 1, 31)),
        ("2026-01-31", date(2026, 1, 31)),
        ("2026-01-31 00:00:00", date(2026, 1, 31)),
        ("31/01/2026", date(2026, 1, 31)),
        ("1/2/2026", date(2026, 2, 1)),  # day first
        ("31-01-2026", date(2026, 1, 31)),
        ("31.01.2026", date(2026, 1, 31)),
        (" 2026-01-31 ", date(2026, 1, 31)),
    ],
)
def test_parse_date_accepts_common_inputs(value, expected):
    assert parse_date(value) == expected


def test_parse_date_converts_excel_serial_numbers():
    serial = to_excel(datetime(2026, 1, 1))
    assert parse_date(serial) == date(2026, 1, 1)
    assert parse_date(int(serial)) == date(2026, 1, 1)
    assert parse_date(str(int(serial))) == date(2026, 1, 1)


@pytest.mark.parametrize(
    "value",
    ["", "abc", None, True, "2026-02-30", "31/13/2026", "01/01/1800", "01/01/2569", 5, "2026"],
)
def test_parse_date_rejects_garbage_instead_of_crashing(value):
    with pytest.raises(DateError):
        parse_date(value)


def test_buddhist_year_input_is_rejected_with_a_helpful_message():
    with pytest.raises(DateError) as info:
        parse_date("01/01/2569")
    assert "พ.ศ." in str(info.value)
