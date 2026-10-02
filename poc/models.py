from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LetterData:
    source_row: int
    customer_name: str
    policy_number: str
    coverage_start_date: datetime
    coverage_end_date: datetime
    hospital_name: str
    requested_documents: tuple[str, ...]


@dataclass(frozen=True)
class RowIssue:
    source_row: int
    field: str
    code: str
    message: str

