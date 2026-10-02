"""Run the REAL as2 validator on a workbook and print its exact output (read-only use of as2)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "as2" / "poc"))
from validation import load_and_validate, FileValidationError  # noqa: E402

path = Path(sys.argv[1])
try:
    letters, issues, skipped = load_and_validate(path)
except FileValidationError as exc:
    print("FILE ERROR:", exc); sys.exit(1)
print(f"{path.name}: eligible={len(letters)} rejected_rows={len({i.source_row for i in issues})} skipped={len(skipped)}")
for i in issues:
    print(f"  row {i.source_row} | {i.field} | {i.code} | {i.message}")
for s in skipped:
    print(f"  skip row {s['source_row']} | {s['reason']}")
if len(sys.argv) > 2:
    rows = [{"source_row": l.source_row, "customer_name": l.customer_name, "policy_number": l.policy_number,
             "start": l.coverage_start_date.isoformat(), "end": l.coverage_end_date.isoformat(),
             "hospital_name": l.hospital_name, "documents": list(l.requested_documents)} for l in letters]
    Path(sys.argv[2]).write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
