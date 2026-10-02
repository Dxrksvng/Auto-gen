"""Shared pytest setup: make the POC modules importable from tests."""

import sys
from pathlib import Path

POC_DIR = Path(__file__).resolve().parents[1]
if str(POC_DIR) not in sys.path:
    sys.path.insert(0, str(POC_DIR))


def make_xlsx(path, rows, headers=None, sheet_title="Sheet1"):
    """Write a small workbook for tests. ``rows`` are lists in the 7 data columns."""
    from openpyxl import Workbook

    from validation import HEADERS

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_title
    sheet.append(list(headers if headers is not None else HEADERS))
    for row in rows:
        sheet.append(row)
    workbook.save(path)
    return path
