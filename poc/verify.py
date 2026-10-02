"""Verify a rendered letter against the EXPECTED full text built from its row.

The check is on text, not "value in text": every expected block (salutation, date
sentence, hospital sentence, each numbered item, closing, ...) must be present, and
known defects (doubled words, leftover placeholders, wrong date format, wrong item
count, banner in the wrong mode) must be absent.

Comparison ignores whitespace and line wrapping and applies NFKC, because PDF text
extractors return Thai text with arbitrary line breaks and may split "ำ" into
nikhahit + sara aa. A visual check of the PNGs is still needed for tone-mark
placement (see docs/A2_CHANGELOG.md): text extraction cannot see glyph positions.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pymupdf

from letter import LetterConfig, LetterText, build_letter_text, load_letter_config
from models import LetterData

_NUMBERED_LINE = re.compile(r"^\s*(\d{1,3})\.(?!\d)")
_GREGORIAN_DATE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b")
# (text as it would be seen in the PDF, what to show the operator)
_FORBIDDEN = (("คุณคุณ", "คุณ คุณ"), ("โรงพยาบาลโรงพยาบาล", "โรงพยาบาล โรงพยาบาล"),
              ("{{", "{{"), ("}}", "}}"), ("<", "<"), (">", ">"))  # fmt: skip


class VerificationError(Exception):
    """The PDF does not match the row it was generated from."""

    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = problems


def _compact(text: str) -> str:
    return "".join(unicodedata.normalize("NFKC", text).split())


def _expected_blocks(content: LetterText) -> list[tuple[str, str]]:
    blocks = [
        ("ผู้รับจดหมาย", content.recipient_line),
        ("หัวเรื่อง", content.subject_line),
        ("ย่อหน้าแรก (เลขกรมธรรม์ ชื่อบริษัท และวันที่คุ้มครอง)", content.intro),
        ("ย่อหน้าโรงพยาบาล", content.request),
    ]
    blocks += [(f"รายการที่ {number}", item) for number, item in enumerate(content.items, start=1)]
    blocks += [("ย่อหน้าช่องทางส่งเอกสาร", content.submit), ("ย่อหน้าติดต่อ", content.contact), ("ท้ายจดหมาย", content.closing)]
    return blocks


def check_text(text: str, letter: LetterData, config: LetterConfig | None = None, preview: bool = False) -> list[str]:
    """Return a list of problems (empty list = the text matches the row)."""
    config = config or load_letter_config()
    content = build_letter_text(letter, config, preview=preview)
    seen = _compact(text)
    problems: list[str] = []

    expected_compact = ""
    for label, block in _expected_blocks(content):
        expected_compact += _compact(block)
        if _compact(block) not in seen:
            problems.append(f"ไม่พบข้อความที่คาดไว้ใน PDF: {label}: {block[:70]}")

    banner_text = _compact(config.preview_banner)
    if preview and banner_text not in seen:
        problems.append("ไม่พบแบนเนอร์ตัวอย่างในโหมด preview")
    if not preview and banner_text in seen:
        problems.append("พบแบนเนอร์ตัวอย่างในฉบับจริง (ต้องมีเฉพาะโหมด preview)")

    for needle, shown in _FORBIDDEN:
        if needle in seen and needle not in expected_compact:
            problems.append(f"พบข้อความที่ไม่ควรมี: {shown}")
    for match in _GREGORIAN_DATE.findall(text):
        if match not in " ".join(block for _, block in _expected_blocks(content)):
            problems.append(f"พบวันที่รูปแบบ dd/mm/yyyy ({match}) ต้องเป็นวันที่ พ.ศ. แบบตัวอักษร เช่น 1 มกราคม 2569")

    numbers = [int(m.group(1)) for line in text.splitlines() if (m := _NUMBERED_LINE.match(line))]
    expected_numbers = list(range(1, len(content.items) + 1))
    if sorted(numbers) != expected_numbers:
        problems.append(f"จำนวนรายการเอกสารไม่ตรง: คาดว่าจะมี {len(expected_numbers)} รายการ แต่พบเลขข้อ {sorted(numbers)}")
    return problems


def extract_text(path: Path) -> tuple[str, list[str]]:
    """Return (all page text, names of embedded fonts)."""
    with pymupdf.open(path) as doc:
        if doc.page_count < 1:
            raise VerificationError(["PDF ไม่มีหน้า"])
        text = "\n".join(page.get_text() for page in doc)
        fonts = sorted({font[3] for page in doc for font in page.get_fonts()})
    return text, fonts


def verify_pdf(path: Path, letter: LetterData, config: LetterConfig | None = None, preview: bool = False) -> None:
    """Raise VerificationError if the PDF does not match the row."""
    text, fonts = extract_text(Path(path))
    problems = check_text(text, letter, config, preview=preview)
    if not any("Sarabun" in name for name in fonts):
        problems.append(f"ฟอนต์ภาษาไทย Sarabun ไม่ได้ถูกฝังใน PDF (พบ: {', '.join(fonts) or 'ไม่มี'})")
    if problems:
        raise VerificationError(problems)
