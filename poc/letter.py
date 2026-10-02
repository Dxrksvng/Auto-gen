"""Letter content: the single source of truth for what a letter says.

The renderer prints this content and the verifier checks the finished PDF against the
same content, so the two cannot drift apart. Wording lives in config/letter.yml.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from models import LetterData
from normalize import th_date

DEFAULT_LETTER_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "letter.yml"


@dataclass(frozen=True)
class LetterConfig:
    template_version: str
    company_name_th: str
    app_name: str
    contact_place: str
    subject: str
    paragraphs: dict[str, str]
    preview_banner: str


@dataclass(frozen=True)
class LetterText:
    """Every visible text block of one letter, in reading order."""

    banner: str | None
    recipient_line: str  # "เรียน คุณสมชาย ใจดี"
    subject_line: str  # "เรื่อง การแจ้งขอเอกสารเพิ่มเติม"
    intro: str
    request: str
    items: tuple[str, ...]  # "1. <document>", "2. <document>", ...
    submit: str
    contact: str
    closing: str


def load_letter_config(path: Path | None = None) -> LetterConfig:
    raw = yaml.safe_load((path or DEFAULT_LETTER_CONFIG_PATH).read_text(encoding="utf-8"))
    company = raw["company"]
    return LetterConfig(
        template_version=raw["template_version"],
        company_name_th=company["name_th"],
        app_name=company["app_name"],
        contact_place=company["contact_place"],
        subject=raw["subject"],
        paragraphs={key: " ".join(str(value).split()) for key, value in raw["paragraphs"].items()},
        preview_banner=raw["preview_banner"],
    )


def build_letter_text(letter: LetterData, config: LetterConfig, preview: bool = False) -> LetterText:
    """Fill the template wording with one row. Pure function, no I/O."""
    fields = {
        "policy_number": letter.policy_number,
        "company_name": config.company_name_th,
        "coverage_start": th_date(letter.coverage_start_date),
        "coverage_end": th_date(letter.coverage_end_date),
        "hospital": letter.hospital,
        "app_name": config.app_name,
        "contact_place": config.contact_place,
    }
    p = config.paragraphs
    return LetterText(
        banner=config.preview_banner if preview else None,
        recipient_line=f"เรียน {letter.salutation}",
        subject_line=f"เรื่อง {config.subject}",
        intro=p["intro"].format(**fields),
        request=p["request"].format(**fields),
        items=tuple(f"{number}. {name}" for number, name in enumerate(letter.requested_documents, start=1)),
        submit=p["submit"].format(**fields),
        contact=p["contact"].format(**fields),
        closing=p["closing"],
    )
