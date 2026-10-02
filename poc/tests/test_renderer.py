"""A8/A9: Thai PDF rendering with a bundled open font, template layout, preview banner."""

import os
import re
import shutil
from datetime import date
from pathlib import Path

import fitz
import pytest

from letter import load_letter_config
from models import LetterData
from renderer import RendererUnavailableError, build_html, find_chrome, render_letter

POC = Path(__file__).resolve().parents[1]
CONFIG = load_letter_config()


def sample(**overrides):
    values = {
        "source_row": 2, "customer_name": "คุณสมชาย ใจดี", "salutation": "คุณสมชาย ใจดี",
        "policy_number": "POL-2026-000123", "coverage_start_date": date(2026, 1, 1),
        "coverage_end_date": date(2026, 12, 31), "hospital_name": "โรงพยาบาลกรุงเทพ", "hospital": "โรงพยาบาลกรุงเทพ",
        "requested_documents": ("สำเนาใบเสร็จค่ารักษาพยาบาล", "รายงานทางการแพทย์"),
    }  # fmt: skip
    values.update(overrides)
    return LetterData(**values)


def chrome_available():
    try:
        find_chrome()
    except RendererUnavailableError:
        return False
    return True


needs_chrome = pytest.mark.skipif(not chrome_available(), reason="Chrome/Chromium not found (set CHROME_BIN)")


def pdf_text(path):
    return "\n".join(page.get_text() for page in fitz.open(path))


def test_bundled_thai_font_and_its_license_are_present():
    fonts = POC / "assets" / "fonts"
    assert (fonts / "Sarabun-Regular.ttf").stat().st_size > 10_000
    assert (fonts / "Sarabun-Bold.ttf").stat().st_size > 10_000
    assert "SIL OPEN FONT LICENSE" in (fonts / "OFL.txt").read_text(encoding="utf-8")


def test_no_platform_specific_font_paths_in_source():
    for path in POC.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "/System/Library" not in text, path.name
        assert "C:\\\\Windows" not in text, path.name


def test_html_escapes_data_instead_of_interpreting_markup():
    html = build_html(sample(hospital="รพ. <foo> & <b>x</b>"), CONFIG)
    assert "&lt;foo&gt;" in html
    assert "&amp;" in html
    assert "<foo>" not in html
    assert "<b>x</b>" not in html


def test_html_uses_relative_bundled_assets_not_system_fonts():
    html = build_html(sample(), CONFIG)
    assert "Sarabun-Regular.ttf" in html
    assert "logo.png" in html


def test_banner_only_in_preview_mode():
    normal = build_html(sample(), CONFIG)
    preview = build_html(sample(), CONFIG, preview=True)
    assert CONFIG.preview_banner not in normal
    assert CONFIG.preview_banner in preview


def test_html_contains_template_blocks_in_order():
    html = build_html(sample(), CONFIG).split("<body>")[1]  # the <title> repeats the subject
    order = ["logo.png", "เรียน", "เรื่อง", "ตามที่ท่านได้ทำประกันสุขภาพ", "ดังนี้", "ท่านสามารถแนบเอกสาร", "จึงเรียนมาเพื่อโปรดทราบ"]
    positions = [html.index(token) for token in order]
    assert positions == sorted(positions)


def test_missing_chrome_gives_a_clear_error(monkeypatch):
    monkeypatch.setenv("CHROME_BIN", "/nonexistent/chrome")
    monkeypatch.setattr(shutil, "which", lambda _name: None)
    with pytest.raises(RendererUnavailableError) as info:
        find_chrome()
    assert "CHROME_BIN" in str(info.value)


@needs_chrome
def test_render_creates_one_page_pdf_with_embedded_sarabun_and_logo(tmp_path):
    out = tmp_path / "letter.pdf"
    render_letter(sample(), out)
    assert out.exists()
    assert not list(tmp_path.glob("*.tmp*"))
    doc = fitz.open(out)
    assert doc.page_count == 1
    assert any("Sarabun" in font[3] for font in doc[0].get_fonts())
    assert doc[0].get_images(), "logo image should be on the page"


@needs_chrome
def test_rendered_text_has_thai_dates_and_no_banner(tmp_path):
    out = tmp_path / "letter.pdf"
    render_letter(sample(), out)
    compact = "".join(pdf_text(out).split())
    assert "1มกราคม2569" in compact
    assert "31ธันวาคม2570" not in compact
    assert "".join(CONFIG.preview_banner.split()) not in compact
    assert "คุณคุณ" not in compact


@needs_chrome
def test_preview_pdf_carries_the_banner(tmp_path):
    out = tmp_path / "preview.pdf"
    render_letter(sample(), out, preview=True)
    assert "".join(CONFIG.preview_banner.split()) in "".join(pdf_text(out).split())


@needs_chrome
def test_page_one_rasterizes_to_a_non_blank_image(tmp_path):
    out = tmp_path / "letter.pdf"
    render_letter(sample(), out)
    pix = fitz.open(out)[0].get_pixmap(dpi=60)
    assert len(set(pix.samples[::97])) > 3


@pytest.mark.skipif("CHROME_BIN" in os.environ and not Path(os.environ["CHROME_BIN"]).exists(), reason="bad CHROME_BIN")
def test_template_config_corrects_the_known_typo():
    text = " ".join(CONFIG.paragraphs.values())
    assert "ท่านสามารถ" in text
    assert re.search(r"ท่าสามารถ", text) is None
