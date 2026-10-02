"""A7: verify the rendered text against the expected full lines, not 'value in text'."""

import unicodedata
from datetime import date

import pytest

from letter import build_letter_text, load_letter_config
from models import LetterData
from renderer import RendererUnavailableError, find_chrome, render_letter
from verify import VerificationError, check_text, verify_pdf

CONFIG = load_letter_config()


def sample(**overrides):
    values = {
        "source_row": 2, "customer_name": "สมชาย ใจดี", "salutation": "คุณสมชาย ใจดี",
        "policy_number": "POL-2026-000123", "coverage_start_date": date(2026, 1, 1),
        "coverage_end_date": date(2026, 12, 31), "hospital_name": "กรุงเทพ", "hospital": "โรงพยาบาลกรุงเทพ",
        "requested_documents": ("สำเนาใบเสร็จค่ารักษาพยาบาล", "รายงานทางการแพทย์"),
    }  # fmt: skip
    values.update(overrides)
    return LetterData(**values)


def good_text(letter, *, preview=False, wrap_every=None):
    """Text as an extractor would return it: one paragraph per line, optionally wrapped."""
    content = build_letter_text(letter, CONFIG, preview=preview)
    lines = [*([content.banner] if content.banner else []), content.recipient_line, content.subject_line]
    lines += [content.intro, content.request, *content.items, content.submit, content.contact, content.closing]
    if wrap_every:
        lines = [part for line in lines for part in (line[i : i + wrap_every] for i in range(0, len(line), wrap_every))]
    return "\n".join(lines)


def test_correct_text_passes():
    assert check_text(good_text(sample()), sample(), CONFIG) == []


def test_wrapping_and_whitespace_differences_do_not_matter():
    assert check_text(good_text(sample(), wrap_every=17), sample(), CONFIG) == []


def test_decomposed_sara_am_from_the_extractor_still_matches():
    text = unicodedata.normalize("NFKD", good_text(sample()))
    assert "\u0e4d\u0e32" in text  # the extractor returned nikhahit + sara aa
    assert check_text(text, sample(), CONFIG) == []


@pytest.mark.parametrize(
    ("needle", "replacement", "expected_problem"),
    [
        ("คุณสมชาย", "คุณ คุณสมชาย", "คุณ คุณ"),
        ("จากทางโรงพยาบาลกรุงเทพ", "จากทางโรงพยาบาล โรงพยาบาลกรุงเทพ", "โรงพยาบาล โรงพยาบาล"),
        ("1 มกราคม 2569", "01/01/2026", "dd/mm/yyyy"),
        ("POL-2026-000123", "POL-2026-000123 {{x}}", "{{"),
        ("ดังนี้", "ดังนี้ <>", "<"),
    ],
)
def test_known_defects_are_reported(needle, replacement, expected_problem):
    text = good_text(sample()).replace(needle, replacement)
    problems = check_text(text, sample(), CONFIG)
    assert problems, f"defect {expected_problem!r} was not detected"
    assert any(expected_problem in p for p in problems), problems


def test_missing_document_item_is_reported():
    text = good_text(sample()).replace("2. รายงานทางการแพทย์", "")
    assert any("รายการที่ 2" in p for p in check_text(text, sample(), CONFIG))


def test_wrong_number_of_numbered_items_is_reported():
    text = good_text(sample()) + "\n3. เอกสารที่ไม่ควรมี"
    assert any("จำนวนรายการ" in p for p in check_text(text, sample(), CONFIG))


def test_wrong_date_is_reported():
    text = good_text(sample()).replace("31 ธันวาคม 2569", "31 ธันวาคม 2570")
    assert check_text(text, sample(), CONFIG)


def test_banner_is_required_in_preview_and_forbidden_otherwise():
    assert check_text(good_text(sample(), preview=True), sample(), CONFIG, preview=True) == []
    assert any("แบนเนอร์" in p for p in check_text(good_text(sample(), preview=True), sample(), CONFIG))
    assert any("แบนเนอร์" in p for p in check_text(good_text(sample()), sample(), CONFIG, preview=True))


def test_angle_brackets_that_come_from_the_data_are_not_flagged():
    letter = sample(hospital="รพ. <foo> ทดสอบ")
    assert check_text(good_text(letter), letter, CONFIG) == []


def chrome_ok():
    try:
        find_chrome()
    except RendererUnavailableError:
        return False
    return True


needs_chrome = pytest.mark.skipif(not chrome_ok(), reason="Chrome/Chromium not found (set CHROME_BIN)")


@needs_chrome
def test_real_pdf_passes_verification(tmp_path):
    out = tmp_path / "ok.pdf"
    render_letter(sample(), out)
    verify_pdf(out, sample(), CONFIG)


@needs_chrome
def test_long_wrapped_document_name_does_not_fail_a_correct_pdf(tmp_path):
    long_name = "สำเนาใบเสร็จค่ารักษาพยาบาล" * 15  # about 390 characters
    letter = sample(requested_documents=(long_name, "ใบรับรองแพทย์"))
    out = tmp_path / "long.pdf"
    render_letter(letter, out)
    verify_pdf(out, letter, CONFIG)


@needs_chrome
def test_verifier_catches_a_pdf_that_does_not_match_the_row(tmp_path):
    out = tmp_path / "other.pdf"
    render_letter(sample(salutation="คุณคนอื่น"), out)
    with pytest.raises(VerificationError):
        verify_pdf(out, sample(), CONFIG)
