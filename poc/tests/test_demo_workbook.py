"""The demo workbook used in the answer must keep producing the documented classification."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from make_demo_workbook import build  # noqa: E402

from validation import load_and_validate  # noqa: E402


def test_demo_workbook_covers_every_row_outcome(tmp_path):
    result = load_and_validate(build(tmp_path / "demo.xlsx"))
    expected = {"populated": 9, "eligible": 3, "rejected": 3, "skipped": 2, "conflicts": 1, "duplicates": 1}
    assert result.counts() == expected
    assert [letter.source_row for letter in result.letters] == [2, 7, 8]
    assert result.rejected_rows == {5, 6, 10}
    codes = {(i.source_row, i.code) for i in result.issues}
    assert {(3, "DUPLICATE_ROW"), (4, "CONFLICTING_ROW"), (5, "UNKNOWN_DOCUMENT"), (6, "DATE_ORDER"),
            (8, "NAME_FORMAT"), (10, "INVALID_LIST")} <= codes  # fmt: skip
    serial_letter = next(letter for letter in result.letters if letter.source_row == 7)
    assert serial_letter.coverage_start_date.isoformat() == "2026-05-10"
