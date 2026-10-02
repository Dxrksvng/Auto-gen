"""Deterministic normalization of values before they go into a letter.

No LLM is involved anywhere in this module: every rule is explicit, tested and
auditable. Anything the rules do not recognize is kept as-is and reported as a
warning instead of being guessed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

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
