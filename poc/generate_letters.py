"""Command line entry point: Excel in, verified letter PDFs + reports out.

    python generate_letters.py "../data/Example claim table.xlsx"
    python generate_letters.py input.xlsx --preview        # adds the review banner

Every run writes to its own directory, never over a previous run:

    output/run_<UTC timestamp>_<first 8 chars of the file SHA-256>[_preview]/
        letters/*.pdf                       verified letters only
        reports/rejected.csv                rows that were blocked (errors)
        reports/validation_report.csv       every issue: errors, warnings, info
        manifest.json                       counts, reasons, versions, reconciliation

Exit codes: 0 ok, 1 some letter failed, 2 file-level error, 3 Chrome not found.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from letter import LetterConfig, load_letter_config
from models import LetterData
from normalize import DocumentNames, load_document_names
from renderer import FONT_REGULAR, RendererUnavailableError, chrome_version, find_chrome, render_letter
from validation import FileValidationError, load_and_validate
from verify import VerificationError, verify_pdf

REPORT_FIELDS = ["source_row", "severity", "field", "code", "message"]


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def safe_output_name(policy_number: str, source_row: int) -> str:
    """File name from the row number and a hash of the policy number; no customer data."""
    token = hashlib.sha256(policy_number.encode("utf-8")).hexdigest()[:12]
    return f"row_{source_row:04d}_{token}.pdf"


def _atomic_write(path: Path, write) -> None:
    tmp = path.with_name(path.name + ".tmp")
    write(tmp)
    tmp.replace(path)


def _write_json(path: Path, data: dict) -> None:
    _atomic_write(path, lambda tmp: tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"))


def _write_report(path: Path, issues: list) -> None:
    def write(tmp: Path) -> None:
        with tmp.open("w", newline="", encoding="utf-8-sig") as target:
            writer = csv.DictWriter(target, fieldnames=REPORT_FIELDS)
            writer.writeheader()
            writer.writerows({key: asdict(issue)[key] for key in REPORT_FIELDS} for issue in issues)

    _atomic_write(path, write)


def new_run_dir(output_root: Path, now: datetime, file_hash: str, preview: bool) -> Path:
    """Create a fresh run directory; a numeric suffix avoids collisions within one second."""
    base = f"run_{now.strftime('%Y%m%dT%H%M%SZ')}_{file_hash[:8]}" + ("_preview" if preview else "")
    output_root.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, 1000):
        candidate = output_root / (base if attempt == 1 else f"{base}_{attempt}")
        try:
            candidate.mkdir()
        except FileExistsError:
            continue
        (candidate / "letters").mkdir()
        (candidate / "reports").mkdir()
        return candidate
    raise RuntimeError(f"could not create a run directory under {output_root}")


def _generate_one(letter: LetterData, letters_dir: Path, config: LetterConfig, preview: bool) -> dict:
    """Render and verify one letter. Returns a manifest entry; a failed PDF is deleted."""
    name = safe_output_name(letter.policy_number, letter.source_row)
    target = letters_dir / name
    try:
        render_letter(letter, target, config, preview=preview)
        verify_pdf(target, letter, config, preview=preview)
    except VerificationError as exc:
        target.unlink(missing_ok=True)
        return {"source_row": letter.source_row, "error": f"verification: {exc}", "problems": exc.problems}
    except Exception as exc:  # isolate the row: one bad letter must not stop the batch
        target.unlink(missing_ok=True)
        return {"source_row": letter.source_row, "error": f"{type(exc).__name__}: {exc}", "problems": []}
    return {"source_row": letter.source_row, "output": f"letters/{name}", "pdf_sha256": digest(target)}


def run(
    input_path: Path,
    output_root: Path = Path("output"),
    preview: bool = False,
    now: datetime | None = None,
    names: DocumentNames | None = None,
    config: LetterConfig | None = None,
) -> Path:
    """Validate the workbook, generate and verify the letters, write reports. Returns the run dir."""
    input_path, output_root = Path(input_path), Path(output_root)
    config = config or load_letter_config()
    validation = load_and_validate(input_path, names or load_document_names())  # file-level errors raise here
    chrome = find_chrome() if validation.letters else None  # fail before creating a run directory
    file_hash = digest(input_path)
    now = now or datetime.now(UTC)
    run_dir = new_run_dir(output_root, now, file_hash, preview)

    generated, failed = [], []
    for letter in validation.letters:
        entry = _generate_one(letter, run_dir / "letters", config, preview)
        (generated if "output" in entry else failed).append(entry)

    errors = [issue for issue in validation.issues if issue.severity == "error"]
    _write_report(run_dir / "reports" / "rejected.csv", errors)
    _write_report(run_dir / "reports" / "validation_report.csv", validation.issues)

    counts = {**validation.counts(), "generated": len(generated), "failed": len(failed)}
    reconciled = (
        counts["populated"] == counts["rejected"] + counts["skipped"] + counts["duplicates"] + counts["eligible"]
        and counts["eligible"] == counts["generated"] + counts["failed"]
    )
    manifest = {
        "run_id": run_dir.name,
        "mode": "preview" if preview else "normal",
        "source_file": input_path.name,
        "source_sha256": file_hash,
        "generated_at": now.isoformat(),
        "template_version": config.template_version,
        "renderer": {
            "engine": "chrome-headless",
            "chrome_version": chrome_version() if chrome else "not used (no letters)",
            "font": FONT_REGULAR.name,
            "font_sha256": digest(FONT_REGULAR),
        },
        "counts": counts,
        "reconciled": reconciled,
        "generated": generated,
        "failed": failed,
        "skipped": [asdict(s) for s in validation.skipped],
        "duplicates": [asdict(d) for d in validation.duplicates],
        "rejected": [
            {"source_row": row, "codes": sorted({i.code for i in errors if i.source_row == row})}
            for row in sorted(validation.rejected_rows)
        ],
        "notice": "Letters are for review and release by a person; this tool never sends anything to customers.",
    }
    _write_json(run_dir / "manifest.json", manifest)
    return run_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate verified request-for-documents letters from an Excel file")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("output"))
    parser.add_argument("--preview", action="store_true", help="add the review banner (never use for customers)")
    args = parser.parse_args(argv)
    try:
        run_dir = run(args.input, args.output, preview=args.preview)
    except FileValidationError as exc:
        print(f"[{exc.code}] {exc.message}", file=sys.stderr)
        return 2
    except RendererUnavailableError as exc:
        print(f"[RENDERER_UNAVAILABLE] {exc}", file=sys.stderr)
        return 3
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    c = manifest["counts"]
    print(run_dir)
    print(
        f"สร้างจดหมาย {c['generated']} ฉบับ | ข้าม {c['skipped']} แถว (ขัดแย้ง {c['conflicts']}) | "
        f"ต้องแก้ไข {c['rejected']} แถว | แถวซ้ำ {c['duplicates']} แถว | ไม่สำเร็จ {c['failed']} ฉบับ"
    )
    return 1 if c["failed"] else 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUTF8", "1")
    raise SystemExit(main())
