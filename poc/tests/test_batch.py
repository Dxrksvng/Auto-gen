"""A6/A7/A10: run directories, manifest, reports and the full sample pipeline."""

import csv
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from conftest import make_xlsx

import generate_letters
from generate_letters import main, run
from renderer import RenderError, RendererUnavailableError, find_chrome
from validation import FileValidationError, load_and_validate
from verify import VerificationError, verify_pdf

SAMPLE = Path(__file__).resolve().parents[2] / "data" / "Example claim table.xlsx"
D1, D2 = datetime(2026, 1, 1), datetime(2026, 12, 31)  # noqa: DTZ001
NOW = datetime(2026, 10, 2, 9, 30, 15, tzinfo=UTC)


def chrome_ok():
    try:
        find_chrome()
    except RendererUnavailableError:
        return False
    return True


pytestmark = pytest.mark.skipif(not chrome_ok(), reason="Chrome/Chromium not found (set CHROME_BIN)")


def row(name="สมชาย ใจดี", policy="P1", status="REQUEST_DOC", docs=("ใบรับรองแพทย์",), hospital="กรุงเทพ"):
    return [name, policy, D1, D2, hospital, status, json.dumps(list(docs), ensure_ascii=False)]


def manifest_of(run_dir):
    return json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))


def csv_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_sample_workbook_generates_one_verified_letter_per_request_row(tmp_path):
    run_dir = run(SAMPLE, tmp_path, now=NOW)
    manifest = manifest_of(run_dir)
    assert manifest["counts"] == {
        "populated": 10, "eligible": 5, "rejected": 0, "skipped": 5, "conflicts": 0,
        "duplicates": 0, "generated": 5, "failed": 0,
    }  # fmt: skip
    assert manifest["reconciled"] is True
    pdfs = sorted((run_dir / "letters").glob("*.pdf"))
    assert len(pdfs) == 5 == len(manifest["generated"])
    result = load_and_validate(SAMPLE)
    for letter in result.letters:  # independent re-verification of every PDF
        (pdf,) = [p for p in pdfs if f"row_{letter.source_row:04d}_" in p.name]
        verify_pdf(pdf, letter)


def test_run_directory_name_has_timestamp_and_file_hash(tmp_path):
    run_dir = run(SAMPLE, tmp_path, now=NOW)
    file_hash = hashlib.sha256(SAMPLE.read_bytes()).hexdigest()
    assert run_dir.name == f"run_20261002T093015Z_{file_hash[:8]}"
    assert manifest_of(run_dir)["source_sha256"] == file_hash


def test_rerun_never_overwrites_previous_output(tmp_path):
    path = make_xlsx(tmp_path / "in.xlsx", [row()])
    first = run(path, tmp_path / "out", now=NOW)
    before = {p.name: p.stat().st_mtime_ns for p in first.rglob("*") if p.is_file()}
    second = run(path, tmp_path / "out", now=datetime(2026, 10, 2, 9, 31, 0, tzinfo=UTC))
    assert first != second
    assert first.exists() and second.exists()
    assert {p.name: p.stat().st_mtime_ns for p in first.rglob("*") if p.is_file()} == before


def test_two_runs_in_the_same_second_get_distinct_directories(tmp_path):
    path = make_xlsx(tmp_path / "in.xlsx", [row()])
    first = run(path, tmp_path / "out", now=NOW)
    second = run(path, tmp_path / "out", now=NOW)
    assert first != second
    assert second.name.startswith(first.name)


def test_duplicate_and_conflict_rows_are_reported_not_silent(tmp_path):
    rows = [row(), row(), row(policy="P2", status="APPROVED", docs=("ใบรับรองแพทย์",))]
    run_dir = run(make_xlsx(tmp_path / "in.xlsx", rows), tmp_path / "out", now=NOW)
    manifest = manifest_of(run_dir)
    assert manifest["counts"]["generated"] == 1
    assert manifest["counts"]["duplicates"] == 1
    assert manifest["counts"]["conflicts"] == 1
    assert manifest["duplicates"] == [{"source_row": 3, "duplicate_of": 2}]
    report = csv_rows(run_dir / "reports" / "validation_report.csv")
    assert any(r["code"] == "DUPLICATE_ROW" and "2" in r["message"] and "3" in r["message"] for r in report)
    assert any(r["code"] == "CONFLICTING_ROW" and "ข้อมูลขัดแย้ง ตรวจสอบ" in r["message"] for r in report)


def test_unknown_document_row_goes_to_rejected_report_without_a_pdf(tmp_path):
    rows = [row(docs=("Discharge Summary",)), row(policy="P2")]
    run_dir = run(make_xlsx(tmp_path / "in.xlsx", rows), tmp_path / "out", now=NOW)
    rejected = csv_rows(run_dir / "reports" / "rejected.csv")
    assert [(r["source_row"], r["code"]) for r in rejected] == [("2", "UNKNOWN_DOCUMENT")]
    assert "Discharge Summary" in rejected[0]["message"]
    assert len(list((run_dir / "letters").glob("*.pdf"))) == 1
    assert manifest_of(run_dir)["rejected"] == [{"source_row": 2, "codes": ["UNKNOWN_DOCUMENT"]}]


def test_preview_mode_is_marked_in_directory_manifest_and_pdf(tmp_path):
    run_dir = run(make_xlsx(tmp_path / "in.xlsx", [row()]), tmp_path / "out", now=NOW, preview=True)
    assert run_dir.name.endswith("_preview")
    assert manifest_of(run_dir)["mode"] == "preview"
    result = load_and_validate(tmp_path / "in.xlsx")
    (pdf,) = (run_dir / "letters").glob("*.pdf")
    verify_pdf(pdf, result.letters[0], preview=True)


def test_one_failing_row_does_not_stop_the_batch(tmp_path, monkeypatch):
    real_render = generate_letters.render_letter

    def flaky(letter, output_path, *args, **kwargs):
        if letter.source_row == 2:
            raise RenderError("simulated crash")
        return real_render(letter, output_path, *args, **kwargs)

    monkeypatch.setattr(generate_letters, "render_letter", flaky)
    run_dir = run(make_xlsx(tmp_path / "in.xlsx", [row(), row(policy="P2")]), tmp_path / "out", now=NOW)
    manifest = manifest_of(run_dir)
    assert (manifest["counts"]["generated"], manifest["counts"]["failed"]) == (1, 1)
    assert manifest["failed"][0]["source_row"] == 2
    assert "simulated crash" in manifest["failed"][0]["error"]
    assert manifest["reconciled"] is True


def test_verification_failure_is_recorded_with_its_problems_and_the_pdf_is_removed(tmp_path, monkeypatch):
    def reject(*_args, **_kwargs):
        raise VerificationError(["พบข้อความที่ไม่ควรมี: คุณ คุณ"])

    monkeypatch.setattr(generate_letters, "verify_pdf", reject)
    run_dir = run(make_xlsx(tmp_path / "in.xlsx", [row()]), tmp_path / "out", now=NOW)
    manifest = manifest_of(run_dir)
    assert manifest["counts"]["failed"] == 1
    assert manifest["failed"][0]["problems"] == ["พบข้อความที่ไม่ควรมี: คุณ คุณ"]
    assert not list((run_dir / "letters").glob("*.pdf")), "an unverified PDF must not stay in the output"


def test_manifest_records_versions_and_no_temp_files_remain(tmp_path):
    run_dir = run(make_xlsx(tmp_path / "in.xlsx", [row()]), tmp_path / "out", now=NOW)
    manifest = manifest_of(run_dir)
    assert manifest["template_version"] == "request-letter-th-v1"
    assert manifest["renderer"]["font"] == "Sarabun-Regular.ttf"
    assert len(manifest["renderer"]["font_sha256"]) == 64
    assert "Chrome" in manifest["renderer"]["chrome_version"] or "Chromium" in manifest["renderer"]["chrome_version"]
    assert not [p for p in run_dir.rglob("*") if ".tmp" in p.name]


def test_output_file_names_do_not_contain_customer_data(tmp_path):
    path = make_xlsx(tmp_path / "in.xlsx", [row(name="สมชาย ใจดี", policy="SECRET-POLICY-9")])
    run_dir = run(path, tmp_path / "out", now=NOW)
    (pdf,) = (run_dir / "letters").glob("*.pdf")
    assert "SECRET" not in pdf.name
    assert "สมชาย" not in pdf.name
    assert pdf.name.startswith("row_0002_")


def test_file_level_error_creates_no_run_directory(tmp_path):
    bad = make_xlsx(tmp_path / "bad.xlsx", [row()], headers=["a", "b"])
    with pytest.raises(FileValidationError):
        run(bad, tmp_path / "out", now=NOW)
    assert not (tmp_path / "out").exists() or not list((tmp_path / "out").iterdir())


def test_cli_prints_the_run_directory_and_returns_zero(tmp_path, capsys):
    path = make_xlsx(tmp_path / "in.xlsx", [row()])
    assert main([str(path), "--output", str(tmp_path / "out")]) == 0
    out = capsys.readouterr().out
    assert "run_" in out
    assert "สร้างจดหมาย 1 ฉบับ" in out


def test_cli_reports_file_level_errors_with_a_code(tmp_path, capsys):
    bad = make_xlsx(tmp_path / "bad.xlsx", [row()], headers=["a"])
    assert main([str(bad), "--output", str(tmp_path / "out")]) == 2
    assert "HEADERS_MISMATCH" in capsys.readouterr().err


def test_cli_returns_nonzero_when_a_letter_failed(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(generate_letters, "render_letter", lambda *a, **k: (_ for _ in ()).throw(RenderError("x")))
    path = make_xlsx(tmp_path / "in.xlsx", [row()])
    assert main([str(path), "--output", str(tmp_path / "out")]) == 1
    assert "ไม่สำเร็จ 1 ฉบับ" in capsys.readouterr().out

