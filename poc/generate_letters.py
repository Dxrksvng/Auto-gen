#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import fitz

from renderer import TEMPLATE_VERSION, render_letter
from validation import FileValidationError, load_and_validate


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def safe_output_name(policy_number: str, source_row: int) -> str:
    token = hashlib.sha256(policy_number.encode("utf-8")).hexdigest()[:12]
    return f"row_{source_row:04d}_{token}.pdf"


def verify_pdf(path: Path, expected_values: tuple[str, ...]) -> None:
    document = fitz.open(path)
    if document.page_count < 1:
        raise ValueError("PDF has no pages")
    text = "\n".join(page.get_text() for page in document)
    if "< >" in text:
        raise ValueError("PDF contains unresolved placeholder")
    for value in expected_values:
        if value not in text:
            raise ValueError(f"Expected content missing: {value}")


def run(input_path: Path, output_root: Path) -> Path:
    source_hash = digest(input_path)
    batch_id = f"batch_{source_hash[:12]}"
    batch_dir = output_root / batch_id
    letters_dir = batch_dir / "letters"
    batch_dir.mkdir(parents=True, exist_ok=True)
    letters, issues, skipped = load_and_validate(input_path)
    generated, failed = [], []
    for letter in letters:
        output_name = safe_output_name(letter.policy_number, letter.source_row)
        output_path = letters_dir / output_name
        try:
            render_letter(letter, output_path)
            verify_pdf(output_path, (letter.policy_number, letter.customer_name, *letter.requested_documents))
            generated.append({"source_row": letter.source_row, "output": f"letters/{output_name}"})
        except Exception as exc:
            failed.append({"source_row": letter.source_row, "error": str(exc)})

    with (batch_dir / "rejected.csv").open("w", newline="", encoding="utf-8-sig") as target:
        writer = csv.DictWriter(target, fieldnames=["source_row", "field", "code", "message"])
        writer.writeheader()
        writer.writerows(asdict(issue) for issue in issues)
    manifest = {
        "batch_id": batch_id,
        "source_file": input_path.name,
        "source_sha256": source_hash,
        "template_version": TEMPLATE_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "populated": len(letters) + len(issues_by_row(issues)) + len(skipped),
            "eligible": len(letters),
            "rejected": len(issues_by_row(issues)),
            "skipped": len(skipped),
            "generated": len(generated),
            "failed": len(failed),
        },
        "generated": generated,
        "skipped": skipped,
        "failed": failed,
        "notice": "POC output only; business rules and letter wording require approval.",
    }
    (batch_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return batch_dir


def issues_by_row(issues) -> set[int]:
    return {issue.source_row for issue in issues}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Assignment 2 POC letters")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("output"))
    args = parser.parse_args()
    try:
        print(run(args.input, args.output))
    except FileValidationError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

