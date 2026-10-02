"""Check that Assignment 3 claims about Assignment 2 match the A2 code as it is NOW.

Two kinds of output:
  PROBE  = observed state of A2 (may be good or bad; recorded, not asserted)
  CHECK  = a statement made by A3 that must hold (PASS/FAIL)

Run with the A2 virtualenv (it has openpyxl, pymupdf, pyyaml, pytest) and Chrome installed:
  ../as2/poc/.venv/bin/python scripts/check_a2_a3.py

Writes docs/a2_a3_check_results.json. Re-run after A2 changes: probes that flip tell you which
A3 statements about A2 must be updated. Nothing is written inside as2/ (temp dir only).
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
ROOT = Path(__file__).resolve().parent.parent  # as3/
A2 = ROOT.parent if (ROOT.parent / "poc").is_dir() else ROOT.parent / "as2"  # as3/ lives inside the A2 repo, or beside it
POC = A2 / "poc"
sys.path.insert(0, str(POC))

results = {"generated_at_utc": datetime.now(timezone.utc).isoformat(), "probes": {}, "checks": {}}
fail = 0


def probe(pid: str, observed, note: str = "") -> None:
    results["probes"][pid] = {"observed": observed, "note": note}
    print(f"PROBE {pid}: {observed}  {note}")


def check(cid: str, ok: bool, note: str = "") -> None:
    global fail
    results["checks"][cid] = {"ok": bool(ok), "note": note}
    fail += not ok
    print(f"{'PASS ' if ok else 'FAIL '}{cid}  {note}")


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def lines_of(p: Path) -> list[str]:
    return read(p).splitlines()


CODE = {n: POC / n for n in ("validation.py", "generate_letters.py", "renderer.py", "models.py", "verify.py", "normalize.py", "letter.py")}
CODE["config/letter.yml"] = POC / "config" / "letter.yml"
src = {n: read(p) for n, p in CODE.items()}
py_src = "\n".join(v for k, v in src.items() if k.endswith(".py"))

# ---------------------------------------------------------------- static probes
probe("P01_a2_changelog_exists", (A2 / "docs" / "A2_CHANGELOG.md").exists())
probe("P02_requirements_files_in_poc", sorted(f for f in ("requirements.txt", "requirements-dev.txt", "pyproject.toml") if (POC / f).exists()))
probe("P03_bundled_font_and_license", all((POC / "assets" / "fonts" / f).exists() for f in ("Sarabun-Regular.ttf", "Sarabun-Bold.ttf", "OFL.txt"))
      and "/System/Library" not in src["renderer.py"], "ฟอนต์แพ็กมากับโค้ด และไม่มี path ของ macOS ใน renderer.py")
probe("P04_manifest_and_reports_atomic", "_atomic_write" in src["generate_letters.py"] and src["generate_letters.py"].count("_atomic_write(") >= 1
      and "_write_json(run_dir" in src["generate_letters.py"] and "_write_report(run_dir" in src["generate_letters.py"])
probe("P05_pdf_written_atomically", "tmp_pdf.replace(output_path)" in src["renderer.py"])
probe("P06_per_row_isolation", bool(re.search(r"except Exception.*?isolate", src["generate_letters.py"], re.S)))
probe("P07_verify_checks", {"expected_blocks": "_expected_blocks" in src["verify.py"], "doubled_words": "_FORBIDDEN" in src["verify.py"],
                            "date_format": "dd/mm/yyyy" in src["verify.py"], "item_count": "expected_numbers" in src["verify.py"],
                            "font_embedded": "Sarabun" in src["verify.py"]}, "ตัวตรวจหลังสร้างของ A2 ตรวจอะไรบ้าง")
non_test = py_src
probe("P08_audit_approval_permission_code", sorted(set(re.findall(r"\b(audit|permission|role|login|auth|approved_by|approve|approver)\b", non_test, re.I))),
      "คำที่เกี่ยวกับ audit/สิทธิ์/อนุมัติ ในโค้ด A2 (ว่าง = ไม่มี)")
probe("P09_a2_is_cli_only", "argparse" in src["generate_letters.py"] and not re.search(r"fastapi|flask|django|uvicorn", non_test, re.I))

# ---------------------------------------------------------------- run A2 for real (temp dir)
import pymupdf  # noqa: E402
from openpyxl import Workbook  # noqa: E402

from generate_letters import run  # noqa: E402
from validation import HEADERS, OBSERVED_STATUSES, load_and_validate  # noqa: E402

tmp = Path(tempfile.mkdtemp(prefix="a2a3_"))
sample = A2 / "data" / "Example claim table.xlsx"


def pdf_text(p: Path) -> str:
    with pymupdf.open(p) as d:
        return "\n".join(pg.get_text() for pg in d)


def pdf_fonts(p: Path) -> list[str]:
    with pymupdf.open(p) as d:
        return sorted({f[3] for pg in d for f in pg.get_fonts()})


def manifest_of(run_dir: Path) -> dict:
    return json.loads(read(run_dir / "manifest.json"))


b1 = run(sample, tmp / "out")
m1 = manifest_of(b1)
pdfs = sorted((b1 / "letters").glob("*.pdf"))
texts = [pdf_text(p) for p in pdfs]
probe("P10_honorific_doubled_in_pdf", any(re.search(r"คุณ\s*คุณ", t) for t in texts), "False = ไม่มีคำนำหน้าซ้ำในจดหมายทั้ง %d ฉบับ" % len(pdfs))
probe("P11_hospital_prefix_doubled_in_pdf", any(re.search(r"โรงพยาบาล\s*โรงพยาบาล", t) for t in texts))
months = "มกราคม|กุมภาพันธ์|มีนาคม|เมษายน|พฤษภาคม|มิถุนายน|กรกฎาคม|สิงหาคม|กันยายน|ตุลาคม|พฤศจิกายน|ธันวาคม"
probe("P12_date_format_in_pdf", (re.search(rf"\d{{1,2}}\s+({months})\s+25\d\d", texts[0]) or re.search(r"\d\d/\d\d/\d{4}", texts[0])).group(0), "รูปแบบวันที่ที่พิมพ์ (พ.ศ. แบบตัวอักษรถ้าตรง)")
probe("P13_letter_has_company_text", any("จำกัด" in t for t in texts), "ข้อความบริษัทตามแบบฟอร์มในจดหมาย")
probe("P14_manifest_keys", {"keys": sorted(m1), "count_keys": sorted(m1["counts"]), "counts": m1["counts"], "reconciled": m1["reconciled"]})
probe("P15_a2_pdf_fonts", pdf_fonts(pdfs[0]), "XXXXXX+ชื่อ = ฝังแบบ subset")

h1 = (b1 / "manifest.json").read_bytes()
time.sleep(1.1)
b2 = run(sample, tmp / "out")
m2 = manifest_of(b2)
probe("P16_rerun_opens_new_directory_and_keeps_old", b1 != b2 and (b1 / "manifest.json").read_bytes() == h1,
      f"โฟลเดอร์ {b1.name} / {b2.name} ; manifest รอบแรกไม่ถูกแก้")
probe("P17_manifest_mentions_previous_run", [k for k in m2 if re.search(r"previous|prior|history|last_run", k, re.I)], "ฟิลด์ที่อ้างถึงรอบก่อน (ว่าง = ไม่มี)")

# one workbook with several problems
wb = Workbook()
ws = wb.active
ws.title = "Sheet1"
ws.append(list(HEADERS))
d1, d2 = datetime(2026, 1, 1), datetime(2026, 12, 31)
ws.append(["คุณก ทดสอบ", "P1", d1, d2, "รพ. <foo> ทดสอบ", "REQUEST_DOC", '["ใบรับรองแพทย์"]'])      # row 2: valid, hospital has markup
ws.append(["คุณก ทดสอบ", "P1", d1, d2, "รพ. <foo> ทดสอบ", "REQUEST_DOC", '["ใบรับรองแพทย์"]'])      # row 3: identical -> duplicate
ws.append(["คุณข ทดสอบ", "P2", d1, d2, "โรงพยาบาลข", "APPROVED", '["ใบรับรองแพทย์"]'])              # row 4: conflict
ws.append(["คุณค ทดสอบ", "P3", d1, d2, "โรงพยาบาลค", "REQUEST_DOC", '["เอกสารที่ไม่มีในรายการ"]'])  # row 5: unknown document name
ws.append(["คุณง ทดสอบ", "P4", datetime(2569, 1, 1), datetime(2570, 1, 1), "โรงพยาบาลง", "REQUEST_DOC", '["ใบรับรองแพทย์"]'])  # row 6: BE year typed as date
edge = tmp / "edge.xlsx"
wb.save(edge)
be = run(edge, tmp / "out_edge")
me = manifest_of(be)
vr = load_and_validate(edge)
codes = {(i.source_row, i.code, i.severity) for i in vr.issues}
epdf = next(iter((be / "letters").glob("*.pdf")), None)
probe("P18_markup_in_data_survives_in_pdf", bool(epdf) and "<foo>" in pdf_text(epdf), "True = ข้อมูลที่มี <...> ถูก escape และพิมพ์ครบ")
probe("P19_identical_rows_one_letter", me["counts"]["duplicates"] == 1 and me["counts"]["generated"] == 1, f"counts={me['counts']}")
probe("P20_status_list_conflict_reported", me["counts"]["conflicts"] == 1 and (4, "CONFLICTING_ROW", "warning") in codes)
b3 = run(edge, tmp / "out_edge")  # same file again, same output root
m3 = manifest_of(b3)
probe("P21_cross_run_duplicate_detected", m3["counts"]["generated"] != me["counts"]["generated"] or bool(m3.get("duplicates_from_previous_runs")),
      f"รอบที่ 1 สร้าง {me['counts']['generated']} รอบที่ 2 สร้าง {m3['counts']['generated']} (เท่ากัน = ไม่เทียบข้ามรอบ)")
probe("P23_unknown_document_rejected", (5, "UNKNOWN_DOCUMENT", "error") in codes)
probe("P24_buddhist_year_in_date_cell_rejected", (6, "INVALID_DATE", "error") in codes)

# A2's own tests, in the interpreter that has A2 dependencies
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(POC / "tests")], capture_output=True, text=True, cwd=str(POC),
                   env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
summary = next((ln for ln in reversed(r.stdout.strip().splitlines()) if "passed" in ln or "failed" in ln or "error" in ln), r.stderr[-200:])
probe("P22_a2_pytest_summary", summary)
passed_n = int(re.search(r"(\d+) passed", summary).group(1)) if re.search(r"(\d+) passed", summary) else -1

# ---------------------------------------------------------------- CHECKS
# C01: every line citation (curated token per range) holds
EXPECT = {
    ("generate_letters.py", 39, 45): "sha256", ("generate_letters.py", 47, 50): "def safe_output_name", ("generate_letters.py", 53, 56): "def _atomic_write",
    ("generate_letters.py", 63, 70): "def _write_report", ("generate_letters.py", 73, 86): "def new_run_dir", ("generate_letters.py", 89, 102): "def _generate_one",
    ("generate_letters.py", 122, 127): "_generate_one", ("generate_letters.py", 128, 129): "rejected.csv", ("generate_letters.py", 132, 161): "reconciled",
    ("generate_letters.py", 165, 191): "def main", ("letter.py", 46, 60): "def load_letter_config", ("config/letter.yml", 11, 11): "template_version",
    ("models.py", 26, 26): "class RowIssue", ("models.py", 37, 50): "class SkippedRow",
    ("normalize.py", 53, 76): "def format_salutation", ("normalize.py", 53, 94): "def hospital", ("normalize.py", 78, 94): "def hospital",
    ("normalize.py", 114, 114): "def th_date", ("normalize.py", 114, 166): "def parse_date", ("normalize.py", 184, 198): "class DocumentNames",
    ("renderer.py", 27, 27): "TEMPLATE_PATH", ("renderer.py", 27, 29): "FONT_REGULAR", ("renderer.py", 28, 28): "FONT_REGULAR", ("renderer.py", 49, 67): "def find_chrome",
    ("renderer.py", 75, 96): "def build_html", ("renderer.py", 151, 171): "def render_letter", ("renderer.py", 165, 165): "tmp_pdf", ("renderer.py", 171, 171): "replace",
    ("validation.py", 33, 41): "HEADERS", ("validation.py", 33, 44): "OBSERVED_STATUSES", ("validation.py", 42, 42): "SHEET_NAME", ("validation.py", 43, 43): "REQUEST_STATUS",
    ("validation.py", 82, 91): "def counts", ("validation.py", 103, 112): "def _parse_document_list", ("validation.py", 114, 176): "def validate_row",
    ("validation.py", 122, 124): '"REQUIRED"', ("validation.py", 122, 153): "REQUIRED_FOR_REQUEST", ("validation.py", 126, 131): "INVALID_DATE", ("validation.py", 132, 138): "DATE_ORDER",
    ("validation.py", 141, 142): "UNKNOWN_STATUS", ("validation.py", 145, 150): "INVALID_LIST", ("validation.py", 151, 153): "REQUIRED_FOR_REQUEST", ("validation.py", 154, 164): "UNKNOWN_DOCUMENT",
    ("validation.py", 204, 313): "def load_and_validate", ("validation.py", 212, 214): "HEADERS_MISMATCH", ("validation.py", 226, 286): "CONFLICTING_ROW",
    ("validation.py", 231, 234): "SkippedRow", ("validation.py", 233, 246): "CONFLICTING_ROW", ("validation.py", 234, 234): "SkippedRow", ("validation.py", 249, 286): "DUPLICATE_ROW",
    ("verify.py", 28, 31): "_FORBIDDEN", ("verify.py", 44, 69): "def _expected_blocks", ("verify.py", 56, 86): "def check_text", ("verify.py", 78, 80): "dd/mm/yyyy",
    ("verify.py", 82, 85): "expected_numbers", ("verify.py", 89, 96): "def extract_text", ("verify.py", 99, 106): "def verify_pdf", ("verify.py", 101, 104): "Sarabun",
}
bad = []
for (f, a, b), token in EXPECT.items():
    chunk = "\n".join(lines_of(CODE[f])[a - 1:b])
    if token not in chunk:
        bad.append(f"{f}:{a}-{b} lacks '{token}'")
check("C01_cited_a2_lines_contain_expected_code", not bad, "; ".join(bad) or f"{len(EXPECT)} line citations verified")

# C02: every cite found in ANSWER.md / definitions is one of the verified ranges (and inside the file)
tok = re.compile(r"`(?:as2/poc/)?((?:config/letter\.yml)|(?:validation|generate_letters|renderer|models|verify|normalize|letter)\.py):(\d+)(?:-(\d+))?`|`:(\d+)(?:-(\d+))?`|(?:as2/poc/)?((?:config/letter\.yml)|(?:validation|generate_letters|renderer|models|verify|normalize|letter)\.py):(\d+)(?:-(\d+))?")
cited, unverified = set(), []
for doc in [ROOT / "ANSWER.md", *sorted((ROOT / "examples" / "definitions").glob("*.yaml"))]:
    last = None
    for m in tok.finditer(read(doc)):
        if m.group(1) or m.group(6):
            last = m.group(1) or m.group(6)
            a = int(m.group(2) or m.group(7))
            b = int(m.group(3) or m.group(8) or a)
        elif last:
            a = int(m.group(4))
            b = int(m.group(5) or a)
        else:
            continue
        cited.add((last, a, b, doc.name))
for f, a, b, name in sorted(cited):
    n = len(lines_of(CODE[f]))
    if not (1 <= a <= b <= n):
        unverified.append(f"{name}: {f}:{a}-{b} outside file ({n} lines)")
    elif (f, a, b) not in EXPECT:
        unverified.append(f"{name}: {f}:{a}-{b} has no verified token")
check("C02_all_cited_ranges_are_verified", not unverified, "; ".join(unverified) or f"{len(cited)} citations, all verified")

# C03: catalog 'a2_code' entries exist verbatim in the A2 file they name
cat = json.loads(read(ROOT / "docs" / "message-catalog.json"))
miss = [m["id"] for m in cat["messages"] + cat["row_chips"] if m["source"] == "a2_code" and m["a2_match"] not in src[m["a2_file"]]]
check("C03_catalog_a2_entries_exist_in_a2_code", not miss, ", ".join(miss) or "ok")

# C04: every code/message the A2 code can produce has a catalog message
import ast as _ast
produced = set()
for _node in _ast.walk(_ast.parse(src["validation.py"])):
    if isinstance(_node, _ast.Call):
        _name = getattr(_node.func, "id", getattr(_node.func, "attr", ""))
        _i = {"add": 1, "RowIssue": 2, "FileValidationError": 0}.get(_name)
        if _i is not None and len(_node.args) > _i and isinstance(_node.args[_i], _ast.Constant):
            produced.add(_node.args[_i].value)
produced |= {"PDF ไม่มีหน้า", "ไม่พบข้อความที่คาดไว้ใน PDF", "พบแบนเนอร์ตัวอย่างในฉบับจริง", "พบข้อความที่ไม่ควรมี", "พบวันที่รูปแบบ", "จำนวนรายการเอกสารไม่ตรง", "ไม่ได้ถูกฝังใน PDF",
             "RendererUnavailableError", "Chrome did not produce a complete PDF"}
verify_strings_ok = all(s in src["verify.py"] or s in src["renderer.py"] for s in list(produced)[:0]) 
matches = [m["a2_match"] for m in cat["messages"] if m.get("a2_match")]
uncovered = sorted(p for p in produced if not any(a in p or p in a for a in matches))
check("C04_every_a2_error_code_has_a_catalog_message", not uncovered, ", ".join(uncovered) or f"{len(produced)} A2 codes/messages covered")

# C05: manifest count keys map to status chips
chip_keys = {"eligible": "READY", "rejected": "FIX", "skipped": "SKIP", "duplicates": "DUP_FILE", "generated": "DONE", "failed": "FAILED"}
have = {c["id"] for c in cat["row_chips"]}
check("C05_manifest_counts_map_to_status_chips", all(k in m1["counts"] and v in have for k, v in chip_keys.items()), "ตรวจกุญแจ counts ของ manifest")

# C06: reconciliation identities stated in the guide hold on real A2 output
def ident(c: dict) -> bool:
    return c["populated"] == c["rejected"] + c["skipped"] + c["duplicates"] + c["eligible"] and c["eligible"] == c["generated"] + c["failed"]
check("C06_guide_identities_hold_on_a2_output", ident(m1["counts"]) and ident(me["counts"]) and m1["reconciled"] and me["reconciled"], f"sample={m1['counts']} edge={me['counts']}")

# C07: sample Excel files behave as the guide says (A2's own validator)
ex = ROOT / "examples"
R1 = load_and_validate(ex / "ตัวอย่างขอเอกสารเพิ่มเติม.xlsx")
R2 = load_and_validate(ex / "ไฟล์ฝึกแก้ไข.xlsx")
R3 = load_and_validate(ex / "แม่แบบขอเอกสารเพิ่มเติม.xlsx")
check("C07_sample_files_match_guide",
      (len(R1.letters), len(R1.skipped), len(R1.rejected_rows)) == (3, 2, 0)
      and (len(R2.letters), len(R2.skipped), sorted(R2.rejected_rows)) == (2, 1, [4, 6, 7])
      and R3.populated == 0,
      f"ตัวอย่าง={R1.counts()} ฝึก rejected={sorted(R2.rejected_rows)}")

# C08: the guide contains every catalog text (whitespace-insensitive)
guide = "".join(read(ROOT / "USER_GUIDE.md").split())
missing = [m["id"] for m in cat["messages"] if "".join(m["message_th"].split()) not in guide]
missing += [c_["id"] for c_ in cat["row_chips"] + cat["run_chips"] if "".join(c_["label_th"].split()) not in guide]
check("C08_guide_contains_all_catalog_statuses_and_messages", not missing, ", ".join(missing) or "ok")

# C09: forbidden-word check on the guide
rc = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_guide_words.py")], capture_output=True, text=True)
check("C09_guide_has_no_forbidden_words", rc.returncode == 0, rc.stdout.strip().splitlines()[-1])

# C10: definition example mirrors A2 headers / statuses / messages
import yaml  # noqa: E402

d = yaml.safe_load(read(ROOT / "examples" / "definitions" / "request_documents.v1.yaml"))
ids = {m["id"] for m in cat["messages"]}
msgs = [r["message"] for r in d["rules"]] + [x["message"] for x in d["output"]["checks_after_render"]] + [d["duplicates"]["message"]]
bad_msgs = sorted(set(m for m in msgs if m not in ids))
check("C10_definition_example_consistent_with_a2",
      tuple(d["source"]["columns"]) == tuple(HEADERS)
      and set(next(f["values"] for f in d["fields"] if f["id"] == "claim_status")) == set(OBSERVED_STATUSES) and not bad_msgs,
      f"columns/statuses ตรง ; message ที่ไม่อยู่ใน catalog: {bad_msgs or 'ไม่มี'}")

# C11: A3 never claims an audit core / that the platform exists
ans = read(ROOT / "ANSWER.md")
banned = [p for p in ("audit core", "แกนตรวจสอบเดิม", "มีอยู่แล้วในระบบ A2 ตรวจสอบย้อนหลัง") if p in ans]
check("C11_answer_has_no_unsupported_audit_claim", not banned, ", ".join(banned) or "ok")

# C12: A3 no longer states A2 defects that A2 has fixed (stale statements)
stale = [p for p in ("A2 **ยังไม่ได้แก้**", "ไม่พบไฟล์นี้", "ผลตรวจ P01", 'TEMPLATE_VERSION = "poc-th-v1"', "ฟอนต์มีเฉพาะเส้นทางของ macOS", "ไม่ escape ข้อมูลก่อนใส่จดหมาย") if p in ans]
check("C12_answer_has_no_stale_a2_defect_claims", not stale, ", ".join(stale) or "ok")

# C13: test count stated in A3 equals the real count
claimed = re.findall(r"(\d+)\s*(?:รายการ)?\s*ผ่าน", ans) + re.findall(r"(\d+) ผ่าน", ans)
stated = {int(x) for x in re.findall(r"\b(\d{2,3}) (?:รายการ)?ผ่าน|\b(\d{2,3}) รายการผ่าน", ans) for x in x if x}
check("C13_test_count_in_answer_matches_real_run", passed_n > 0 and passed_n in {int(x) for x in re.findall(r"(\d{2,3}) (?:รายการ)?(?:ผ่าน)", ans)}, f"จริง={passed_n}")

# C14: A2 claims cited by line in A2's own ANSWER.md exist
a2ans = lines_of(A2 / "ANSWER.md")
check("C14_a2_answer_lines_cited_by_a3", "กันการส่งซ้ำ" in a2ans[157] and "ส่วนที่ยังเป็นการออกแบบ" in a2ans[186], "as2/ANSWER.md:158 และ :187")

(ROOT / "docs" / "a2_a3_check_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
print(f"\n{len(results['checks']) - fail}/{len(results['checks'])} checks passed; {len(results['probes'])} probes recorded")
sys.exit(1 if fail else 0)
