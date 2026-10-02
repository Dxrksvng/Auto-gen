"""Deterministic normalization of values before they go into a letter.

No LLM is involved anywhere in this module: every rule is explicit, tested and
auditable. Anything the rules do not recognize is kept as-is and reported as a
warning instead of being guessed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta

NAME_FORMAT_WARNING = "NAME_FORMAT"

# Honorifics / titles after which "คุณ" must NOT be added. Thai titles are matched
# as prefixes (the source data writes "นายสมชาย" without a space). The list is a
# starting point and is an open question for the business (docs/OPEN_QUESTIONS.md).
THAI_TITLES = (
    "คุณ", "นางสาว", "นาง", "นาย", "น.ส.", "ด.ช.", "ด.ญ.", "เด็กชาย", "เด็กหญิง",
    "ดร.", "ผศ.", "รศ.", "ศ.", "นพ.", "พญ.", "ทพ.", "ทญ.",
)  # fmt: skip
ENGLISH_TITLES = ("mr.", "mrs.", "ms.", "miss", "dr.", "prof.")

HOSPITAL_PREFIXES = ("โรงพยาบาล", "รพ.", "ศูนย์การแพทย์", "คลินิก")
HOSPITAL_DEFAULT_PREFIX = "โรงพยาบาล"

# Thai block, ASCII letters, space, dot, hyphen, apostrophe. Anything else
# (digits, "<", "@", ...) means the name format is not recognized.
_ALLOWED_NAME_CHARS = re.compile(r"^[฀-๿A-Za-z .\-']+$")


@dataclass(frozen=True)
class Salutation:
    text: str
    warning: str | None = None


def clean_text(value: str) -> str:
    """Strip and collapse internal whitespace."""
    return " ".join(value.split())


def _has_known_title(name: str) -> bool:
    lowered = name.casefold()
    return name.startswith(THAI_TITLES) or lowered.startswith(ENGLISH_TITLES)


def format_salutation(name: str) -> Salutation:
    """Return the recipient name with exactly one honorific.

    Rules (in order):
    1. empty name -> ValueError (validation should have rejected the row);
    2. unrecognized characters -> keep as-is and warn, never guess;
    3. already starts with "คุณ" or another known title -> keep;
    4. otherwise prefix "คุณ".
    """
    cleaned = clean_text(name)
    if not cleaned:
        raise ValueError("customer name is empty")
    if not _ALLOWED_NAME_CHARS.match(cleaned):
        return Salutation(cleaned, NAME_FORMAT_WARNING)
    if _has_known_title(cleaned):
        return Salutation(cleaned)
    return Salutation(f"คุณ{cleaned}")


def salutation(name: str) -> str:
    """Text-only convenience wrapper around :func:`format_salutation`."""
    return format_salutation(name).text


def hospital(name: str) -> str:
    """Return the hospital name with the facility word exactly once.

    The letter template reads "จากทาง<hospital>", so the value must carry its own
    facility word. Names that already start with a known facility word are kept;
    bare names get "โรงพยาบาล". Whether the business wants another rule for bare
    names is an open question (docs/OPEN_QUESTIONS.md).
    """
    cleaned = clean_text(name)
    if not cleaned:
        raise ValueError("hospital name is empty")
    if cleaned.startswith(HOSPITAL_PREFIXES):
        return cleaned
    return f"{HOSPITAL_DEFAULT_PREFIX}{cleaned}"


# ---------------------------------------------------------------- dates

THAI_MONTHS = (
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม",
)  # fmt: skip
BUDDHIST_ERA_OFFSET = 543
# Plausible Gregorian year range for coverage dates. Values outside it are rejected
# (fail closed), which also catches Buddhist-era years typed into a Gregorian column.
MIN_YEAR, MAX_YEAR = 1990, 2200
_EXCEL_EPOCH = datetime(1899, 12, 30)  # same convention as openpyxl for 1900-based workbooks
_NUMERIC_TEXT = re.compile(r"^\d+(\.\d+)?$")
_DMY = re.compile(r"^(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{4})$")
_ISO = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?$")


class DateError(ValueError):
    """Raised when a cell cannot be interpreted as a plausible date."""


def th_date(value: date) -> str:
    """Format a date as Thai Buddhist-era text, e.g. "1 มกราคม 2569"."""
    return f"{value.day} {THAI_MONTHS[value.month - 1]} {value.year + BUDDHIST_ERA_OFFSET}"


def _checked(year: int, month: int, day: int) -> date:
    if not MIN_YEAR <= year <= MAX_YEAR:
        raise DateError(
            f"ปี {year} อยู่นอกช่วงที่รองรับ (ค.ศ. {MIN_YEAR}-{MAX_YEAR}) "
            "ถ้าเป็นปี พ.ศ. กรุณาแปลงเป็น ค.ศ."
        )
    try:
        return date(year, month, day)
    except ValueError as exc:
        raise DateError(f"วันที่ไม่มีอยู่จริง: {day}/{month}/{year}") from exc


def _from_serial(number: float) -> date:
    try:
        converted = _EXCEL_EPOCH + timedelta(days=number)
    except OverflowError as exc:
        raise DateError(f"ตัวเลขวันที่ของ Excel ไม่ถูกต้อง: {number}") from exc
    return _checked(converted.year, converted.month, converted.day)


def parse_date(value: object) -> date:
    """Parse a spreadsheet cell into a ``date`` or raise :class:`DateError`.

    Accepts real dates, ISO strings, dd/mm/yyyy (also with - or .), and Excel
    serial numbers (int, float or numeric text). Never guesses month-first.
    """
    if isinstance(value, bool) or value is None:
        raise DateError("ไม่มีค่าวันที่")
    if isinstance(value, datetime):
        return _checked(value.year, value.month, value.day)
    if isinstance(value, date):
        return _checked(value.year, value.month, value.day)
    if isinstance(value, (int, float)):
        return _from_serial(float(value))
    if isinstance(value, str):
        text = value.strip()
        if _NUMERIC_TEXT.match(text):
            return _from_serial(float(text))
        iso = _ISO.match(text)
        if iso:
            return _checked(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))
        dmy = _DMY.match(text)
        if dmy:
            return _checked(int(dmy.group(3)), int(dmy.group(2)), int(dmy.group(1)))
    raise DateError(f"อ่านวันที่ไม่ได้: {value!r}")
