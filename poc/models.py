"""Immutable data carried through the pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LetterData:
    """One validated, normalized row that will become one letter."""

    source_row: int
    customer_name: str  # as in the workbook, whitespace cleaned
    salutation: str  # exactly one honorific, see normalize.format_salutation
    policy_number: str
    coverage_start_date: date
    coverage_end_date: date
    hospital_name: str  # as in the workbook, whitespace cleaned
    hospital: str  # facility word exactly once, see normalize.hospital
    requested_documents: tuple[str, ...]  # approved Thai wording, in source order
    source_documents: tuple[str, ...] = ()  # names as written in the workbook


@dataclass(frozen=True)
class RowIssue:
    """One line of the validation report."""

    source_row: int
    field: str
    code: str
    message: str  # Thai, written for the claims operator
    severity: str = "error"  # "error" blocks the row; "warning" and "info" do not


@dataclass(frozen=True)
class SkippedRow:
    """A valid row that does not produce a letter (status is not REQUEST_DOC)."""

    source_row: int
    reason: str
    conflict: bool = False  # True when documents are listed although no request is made


@dataclass(frozen=True)
class DuplicateRow:
    """A REQUEST_DOC row suppressed because an earlier row is identical."""

    source_row: int
    duplicate_of: int
