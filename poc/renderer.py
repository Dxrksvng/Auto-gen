"""Render one letter to a PDF with an embedded Thai font.

Pipeline: LetterData -> LetterText (letter.py) -> HTML template (escaped) -> headless
Chrome/Chromium "print to PDF". Chrome is used because it breaks Thai text at word
boundaries and writes a PDF whose text can be extracted faithfully (checked in
docs/img and tests); the Thai font is bundled in assets/fonts so the output does not
depend on fonts installed on the machine. No platform-specific font paths are used.
"""

from __future__ import annotations

import html
import os
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path

from letter import LetterConfig, build_letter_text, load_letter_config
from models import LetterData
from normalize import th_date

POC_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = POC_DIR / "templates" / "request_letter_th.html"
FONT_REGULAR = POC_DIR / "assets" / "fonts" / "Sarabun-Regular.ttf"
FONT_BOLD = POC_DIR / "assets" / "fonts" / "Sarabun-Bold.ttf"
LOGO = POC_DIR / "assets" / "logo.png"

CHROME_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome")
CHROME_MAC_PATHS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
)
RENDER_TIMEOUT_SECONDS = 90
POLL_SECONDS = 0.1


class RendererUnavailableError(RuntimeError):
    """No usable Chrome/Chromium binary was found."""


class RenderError(RuntimeError):
    """Chrome ran but did not produce a PDF."""


def find_chrome() -> str:
    """Locate Chrome/Chromium: $CHROME_BIN first, then PATH, then common macOS paths."""
    configured = os.environ.get("CHROME_BIN")
    if configured:
        if Path(configured).exists():
            return configured
        raise RendererUnavailableError(f"CHROME_BIN is set but does not exist: {configured}")
    for name in CHROME_NAMES:
        found = shutil.which(name)
        if found:
            return found
    for candidate in CHROME_MAC_PATHS:
        if Path(candidate).exists():
            return candidate
    raise RendererUnavailableError(
        "Chrome/Chromium not found. Install it (for example `apt install chromium`) "
        "or set CHROME_BIN to the executable."
    )


def chrome_version() -> str:
    """Version string recorded in the run manifest."""
    result = subprocess.run([find_chrome(), "--version"], capture_output=True, text=True, timeout=30, check=False)
    return result.stdout.strip() or "unknown"


def _escape(value: str) -> str:
    return html.escape(value, quote=True)


# Chrome's Thai dictionary does not know most proper nouns and may split them
# mid-word (seen in practice: "เมดพาร์" / "ค" on two lines). Names and numbers that
# must stay readable are therefore kept on one line. Very long values are left
# breakable so a long value can never run past the margin.
NO_BREAK_MAX_CHARS = 40


def _paragraph_html(text: str, protected: tuple[str, ...] = ()) -> str:
    """Escape a paragraph and mark protected values (first occurrence) as non-breaking."""
    escaped = _escape(text)
    for value in protected:
        shown = _escape(value)
        if value and len(value) <= NO_BREAK_MAX_CHARS and shown in escaped:
            escaped = escaped.replace(shown, f'<span class="nb">{shown}</span>', 1)
    return escaped


def build_html(letter: LetterData, config: LetterConfig | None = None, preview: bool = False) -> str:
    """Fill the HTML template. Every value is escaped; data is never interpreted as markup."""
    config = config or load_letter_config()
    content = build_letter_text(letter, config, preview=preview)
    banner = f'<div class="banner">{_escape(content.banner)}</div>' if content.banner else ""
    items = "\n".join(f"<li>{_escape(item)}</li>" for item in content.items)
    slots = {
        "TITLE": _escape(content.subject_line),
        "FONT_REGULAR": FONT_REGULAR.as_uri(),
        "FONT_BOLD": FONT_BOLD.as_uri(),
        "LOGO": LOGO.as_uri(),
        "BANNER": banner,
        "RECIPIENT": _escape(letter.salutation),
        "SUBJECT": _escape(config.subject),
        "INTRO": _paragraph_html(
            content.intro,
            (letter.policy_number, th_date(letter.coverage_start_date), th_date(letter.coverage_end_date)),
        ),
        "REQUEST": _paragraph_html(content.request, (letter.hospital,)),
        "ITEMS": items,
        "SUBMIT": _escape(content.submit),
        "CONTACT": _escape(content.contact),
        "CLOSING": _escape(content.closing),
    }
    page = TEMPLATE_PATH.read_text(encoding="utf-8")
    for name, value in slots.items():
        page = page.replace("{{" + name + "}}", value)
    return page


def _pdf_is_complete(path: Path) -> bool:
    """A PDF is complete when it ends with the %%EOF marker."""
    try:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            handle.seek(max(handle.tell() - 1024, 0))
            return b"%%EOF" in handle.read()
    except OSError:
        return False


def _stop(process: subprocess.Popen) -> None:
    """Terminate Chrome and its helper processes (they live in their own process group)."""
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=5)
            return
        except subprocess.TimeoutExpired:
            continue


def render_letter(
    letter: LetterData,
    output_path: Path,
    config: LetterConfig | None = None,
    preview: bool = False,
) -> None:
    """Write the letter PDF atomically (temp file, then rename).

    Chrome 154 writes the PDF but then keeps running (observed on macOS, also with
    --no-first-run and similar flags), so the PDF is polled until it is complete and
    the Chrome process group is then stopped. A time limit bounds every render.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_pdf = output_path.with_name(output_path.name + ".tmp")
    tmp_pdf.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix="letter_") as workdir:
        page = Path(workdir) / "letter.html"
        page.write_text(build_html(letter, config, preview=preview), encoding="utf-8")
        command = [
            find_chrome(),
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--user-data-dir={Path(workdir) / 'profile'}",
            f"--print-to-pdf={tmp_pdf}",
        ]
        if os.environ.get("CHROME_NO_SANDBOX"):  # needed when running as root inside a container
            command.append("--no-sandbox")
        command.append(page.as_uri())
        process = subprocess.Popen(  # noqa: S603 - fixed argument list, no shell
            command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True
        )
        try:
            deadline = time.monotonic() + RENDER_TIMEOUT_SECONDS
            while time.monotonic() < deadline:
                if tmp_pdf.exists() and _pdf_is_complete(tmp_pdf):
                    break
                if process.poll() is not None and not tmp_pdf.exists():
                    break
                time.sleep(POLL_SECONDS)
        finally:
            _stop(process)
    if not tmp_pdf.exists() or not _pdf_is_complete(tmp_pdf):
        tmp_pdf.unlink(missing_ok=True)
        raise RenderError("Chrome did not produce a complete PDF (timeout or crash)")
    tmp_pdf.replace(output_path)
