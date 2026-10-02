"""Check that Assignment 3 claims about Assignment 2 match the A2 code as it is NOW.

Two kinds of output:
  PROBE  = observed state of A2 (may be good or bad; recorded, not asserted)
  CHECK  = a statement made by A3 that must hold (PASS/FAIL)

Run (needs the A2 POC dependencies):
  uv run --with openpyxl --with pymupdf --with reportlab --with pyyaml --with pytest \
      python scripts/check_a2_a3.py

Writes docs/a2_a3_check_results.json. Re-run after A2 is changed: probes that flip
tell you which A3 statements about A2 must be updated.
"""

import ast
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # as3/
A2 = ROOT.parent / "as2"
POC = A2 / "poc"
sys.path.insert(0, str(POC))

results = {
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "probes": {},
    "checks": {},
}
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


# ---------------------------------------------------------------- A2 state probes
code_files = {
    n: POC / n
    for n in ("validation.py", "generate_letters.py", "renderer.py", "models.py")
}
src = {n: read(p) for n, p in code_files.items()}

probe(
    "P01_a2_changelog_exists",
    (A2 / "docs" / "A2_CHANGELOG.md").exists(),
    "ถ้า False = A2 ยังไม่ถูกบันทึกว่าแก้แล้ว",
)
probe(
    "P02_requirements_file_in_poc",
    any((POC / f).exists() for f in ("requirements.txt", "pyproject.toml")),
)
probe(
    "P03_font_paths_macos_only",
    all(
        p.startswith("/System/Library")
        for p in re.findall(r'Path\("([^"]+)"\)', src["renderer.py"])
    ),
    "FONT_CANDIDATES ทั้งหมดอยู่ใต้ /System/Library",
)
probe(
    "P04_manifest_written_atomically",
    "tmp" in src["generate_letters.py"].split('"manifest.json"')[-1][:80],
    "manifest.json เขียนด้วย write_text ตรง ไม่ใช่เขียนชั่วคราวแล้วเปลี่ยนชื่อ",
)
probe(
    "P05_pdf_written_atomically", "tmp_path.replace(output_path)" in src["renderer.py"]
)
probe(
    "P06_per_row_isolation",
    bool(
        re.search(
            r"try:\s+render_letter.*?except Exception", src["generate_letters.py"], re.S
        )
    ),
)
probe(
    "P07_verify_pdf_checked_fields",
    re.search(
        r"verify_pdf\(output_path, \((.*?)\)\)", src["generate_letters.py"]
    ).group(1),
    "ค่าที่ตรวจในจดหมายหลังสร้าง",
)
non_test = "\n".join(src.values())
probe(
    "P08_audit_approval_permission_code",
    sorted(
        set(
            re.findall(
                r"\b(audit|permission|role|login|auth|approved_by|approve)\b",
                non_test,
                re.I,
            )
        )
    ),
    "คำที่เกี่ยวกับ audit/สิทธิ์/อนุมัติ ในโค้ด A2 (ว่าง = ไม่มี)",
)
probe(
    "P09_a2_is_cli_only",
    "argparse" in src["generate_letters.py"] and "fastapi" not in non_test.lower(),
)

# --- run A2 for real (temp dir)
from openpyxl import Workbook  # noqa: E402
import fitz  # noqa: E402
from generate_letters import run  # noqa: E402
from validation import HEADERS, load_and_validate  # noqa: E402
from models import LetterData  # noqa: E402
from renderer import render_letter  # noqa: E402

tmp = Path(tempfile.mkdtemp(prefix="a2a3_"))
sample = A2 / "data" / "Example claim table.xlsx"


def pdf_text(p: Path) -> str:
    return "\n".join(pg.get_text() for pg in fitz.open(p))


b1 = run(sample, tmp / "out")
manifest1 = json.loads(read(b1 / "manifest.json"))
first_pdf = next(iter(sorted((b1 / "letters").glob("*.pdf"))))
txt = pdf_text(first_pdf)
probe(
    "P10_honorific_doubled_in_pdf",
    "คุณ คุณ" in txt,
    "จดหมายจากไฟล์ตัวอย่างของ Sunday มี 'คุณ คุณ'",
)
probe("P11_hospital_prefix_doubled_in_pdf", "โรงพยาบาล โรงพยาบาล" in txt)
probe(
    "P12_date_format_in_pdf",
    re.search(r"\d\d/\d\d/\d{4}", txt).group(0),
    "รูปแบบวันที่ที่พิมพ์ (ค.ศ. dd/mm/YYYY)",
)
probe(
    "P13_letter_has_company_or_logo_text",
    any(w in txt for w in ("บริษัท", "จำกัด", "ABC")),
    "ข้อความบริษัทจากแบบฟอร์มจริงอยู่ในจดหมายหรือไม่ (False = ไม่ใช่แบบฟอร์มจริง)",
)
probe("P14_manifest_count_keys", sorted(manifest1["counts"].keys()))
probe("P15_manifest_counts_sample", manifest1["counts"])

# fonts: embedded in A2 PDFs? does the post-render check look at fonts?
_fonts = sorted({f[3] for pg in fitz.open(first_pdf) for f in pg.get_fonts()})
probe("P22_a2_pdf_fonts", _fonts, "ฟอนต์ที่อยู่ใน PDF ของ A2 (รูปแบบ XXXXXX+ชื่อ = ฝังแบบ subset)")
_vp = re.search(r"def verify_pdf.*?(?=\ndef )", src["generate_letters.py"], re.S).group(0)
probe("P23_verify_pdf_checks_fonts", "font" in _vp.lower(), "False = ตัวตรวจหลังสร้างของ A2 ไม่ดูฟอนต์เลย")

# rerun
import time  # noqa: E402

time.sleep(1.1)
b2 = run(sample, tmp / "out")
manifest2 = json.loads(read(b2 / "manifest.json"))
probe(
    "P16_rerun_same_directory_overwritten",
    b1 == b2 and manifest1["generated_at"] != manifest2["generated_at"],
    "รันไฟล์เดิมซ้ำ: โฟลเดอร์เดิมถูกใช้และ generated_at ถูกเขียนทับ",
)
probe(
    "P17_manifest_mentions_previous_run",
    any("previous" in k.lower() or "prior" in k.lower() for k in manifest2),
    "manifest มีฟิลด์อ้างถึงรอบก่อนหน้าหรือไม่",
)

# escape / markup
lt = LetterData(
    2,
    "คุณทดสอบ",
    "P1",
    datetime(2026, 1, 1),
    datetime(2026, 12, 31),
    "รพ. <foo> ทดสอบ",
    ("ก",),
)
render_letter(lt, tmp / "esc.pdf")
probe(
    "P18_markup_in_data_survives_in_pdf",
    "<foo>" in pdf_text(tmp / "esc.pdf"),
    "False = ข้อมูลที่มี <...> ถูกกลืน ไม่ได้ escape",
)

# duplicates / conflicts
wb = Workbook()
ws = wb.active
ws.title = "Sheet1"
ws.append(list(HEADERS))
d1, d2 = datetime(2026, 1, 1), datetime(2026, 12, 31)
ws.append(["คุณก", "P1", d1, d2, "โรงพยาบาลก", "REQUEST_DOC", '["เอกสาร"]'])
ws.append(["คุณก", "P1", d1, d2, "โรงพยาบาลก", "REQUEST_DOC", '["เอกสาร"]'])
ws.append(["คุณข", "P2", d1, d2, "โรงพยาบาลข", "APPROVED", '["x"]'])
edge = tmp / "edge.xlsx"
wb.save(edge)
be = run(edge, tmp / "out_edge")
me = json.loads(read(be / "manifest.json"))
probe(
    "P19_identical_rows_both_generated",
    me["counts"]["generated"] == 2,
    "สองแถวเหมือนกันทุกช่องสร้างจดหมายสองฉบับโดยไม่เตือน",
)
probe(
    "P20_status_list_conflict_silently_skipped",
    me["counts"]["skipped"] == 1 and me["counts"]["rejected"] == 0,
    "APPROVED แต่มีรายการเอกสาร ถูกข้ามโดยไม่แจ้ง",
)

# A2 own tests
r = subprocess.run(
    [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        str(POC / "tests"),
    ],
    capture_output=True,
    text=True,
    cwd=str(POC),
)
probe(
    "P21_a2_pytest_summary",
    r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:],
)

# ---------------------------------------------------------------- CHECKS
# C01: line-cited references hold (curated expectations)
EXPECT = [
    ("validation.py", 10, 17, "customer_name"),
    ("validation.py", 19, 19, "OBSERVED_STATUSES"),
    ("validation.py", 26, 26, "def load_and_validate"),
    ("validation.py", 32, 32, "Sheet1"),
    ("validation.py", 42, 43, "HEADERS"),
    ("validation.py", 57, 58, "REQUEST_DOC"),
    ("validation.py", 75, 75, "def validate_row"),
    ("validation.py", 77, 79, "REQUIRED"),
    ("validation.py", 80, 82, "INVALID_DATE"),
    ("validation.py", 83, 85, "DATE_ORDER"),
    ("validation.py", 86, 87, "UNKNOWN_STATUS"),
    ("validation.py", 88, 95, "INVALID_LIST"),
    ("validation.py", 96, 97, "REQUIRED_FOR_REQUEST"),
    ("validation.py", 89, 89, "json.loads"),
    ("validation.py", 60, 60, "json.loads"),
    ("generate_letters.py", 16, 21, "sha256"),
    ("generate_letters.py", 24, 26, "def safe_output_name"),
    ("generate_letters.py", 29, 38, "def verify_pdf"),
    ("generate_letters.py", 31, 32, "no pages"),
    ("generate_letters.py", 34, 35, "unresolved placeholder"),
    ("generate_letters.py", 36, 38, "Expected content missing"),
    ("generate_letters.py", 43, 46, "batch_"),
    ("generate_letters.py", 49, 57, "except Exception"),
    ("generate_letters.py", 59, 62, "rejected.csv"),
    ("generate_letters.py", 63, 82, "manifest"),
    ("generate_letters.py", 90, 90, "def main"),
    ("renderer.py", 14, 14, "TEMPLATE_VERSION"),
    ("renderer.py", 15, 26, "No Thai-capable font found"),
    ("renderer.py", 32, 32, "tmp"),
    ("renderer.py", 36, 36, "%d/%m/%Y"),
    ("renderer.py", 38, 53, "เรียน คุณ"),
    ("renderer.py", 57, 57, "replace"),
    ("renderer.py", 40, 40, "เรียน คุณ"),
    ("renderer.py", 47, 47, "โรงพยาบาล"),
    ("models.py", 5, 13, "class LetterData"),
]
bad = []
for f, a, b, token in EXPECT:
    chunk = "\n".join(lines_of(code_files[f])[a - 1 : b])
    if token not in chunk:
        bad.append(f"{f}:{a}-{b} lacks '{token}'")
check(
    "C01_cited_a2_lines_contain_expected_code",
    not bad,
    "; ".join(bad) or f"{len(EXPECT)} line citations verified",
)

# C02: every a2 path:line cited in ANSWER.md / YAML points inside the file
cited = []
for doc in [
    ROOT / "ANSWER.md",
    *sorted((ROOT / "examples" / "definitions").glob("*.yaml")),
]:
    if doc.exists():
        for m in re.finditer(
            r"(?:as2/poc/)?(validation|generate_letters|renderer|models)\.py:(\d+)(?:-(\d+))?",
            read(doc),
        ):
            f = m.group(1) + ".py"
            a = int(m.group(2))
            b = int(m.group(3) or a)
            n = len(lines_of(code_files[f]))
            if not (1 <= a <= b <= n):
                cited.append(f"{doc.name}: {f}:{a}-{b} outside file ({n} lines)")
check("C02_all_cited_line_numbers_inside_files", not cited, "; ".join(cited) or "ok")

# C03: catalog 'a2_code' entries exist verbatim in the A2 file named
cat = json.loads(read(ROOT / "docs" / "message-catalog.json"))
miss = []
for m in cat["messages"] + cat["row_chips"]:
    if m["source"] == "a2_code":
        if m["a2_match"] not in src[m["a2_file"]]:
            miss.append(m["id"])
check("C03_catalog_a2_entries_exist_in_a2_code", not miss, ", ".join(miss) or "ok")

# C04: every code/message the A2 code can produce is in the catalog (no silent status)
produced = set(
    re.findall(r'RowIssue\([^,]+,[^,]+,\s*"([A-Z_]+)"', src["validation.py"])
)
produced |= set(re.findall(r'FileValidationError\(f?"([^"{]+)', src["validation.py"]))
produced |= set(
    re.findall(r'raise ValueError\(f?"([^"{]+)', src["generate_letters.py"])
)
produced |= set(re.findall(r'RuntimeError\("([^"]+)"', src["renderer.py"]))
match_list = [m["a2_match"] for m in cat["messages"] if m.get("a2_match")]
produced = {p.strip().rstrip(": ").strip() for p in produced}
# covered = a catalog a2_match is contained in the produced string, or vice versa
uncovered = sorted(
    p for p in produced if p and not any(a in p or p in a for a in match_list)
)
check(
    "C04_every_a2_error_string_has_a_catalog_message",
    not uncovered,
    ", ".join(uncovered) or f"{len(produced)} A2 strings covered",
)

# C05: manifest count keys map to chips
chip_keys = {
    "eligible": "READY",
    "rejected": "FIX",
    "skipped": "SKIP",
    "generated": "DONE",
    "failed": "FAILED",
}
have = {c["id"] for c in cat["row_chips"]}
check(
    "C05_manifest_counts_map_to_status_chips",
    all(k in manifest1["counts"] and v in have for k, v in chip_keys.items()),
    "populated = ทั้งหมด",
)

# C06: reconciliation identity stated in the guide holds on real A2 output
c = manifest1["counts"]
c2 = me["counts"]
check(
    "C06_guide_identities_hold_on_a2_output",
    c["populated"] == c["eligible"] + c["rejected"] + c["skipped"]
    and c["eligible"] == c["generated"] + c["failed"]
    and c2["populated"] == c2["eligible"] + c2["rejected"] + c2["skipped"]
    and c2["eligible"] == c2["generated"] + c2["failed"],
    f"sample={c}",
)

# C07: sample Excel files behave as the guide says (validated by A2 validator)
ex = ROOT / "examples"
L, I, S = load_and_validate(ex / "ตัวอย่างขอเอกสารเพิ่มเติม.xlsx")
L2, I2, S2 = load_and_validate(ex / "ไฟล์ฝึกแก้ไข.xlsx")
L3, I3, S3 = load_and_validate(ex / "แม่แบบขอเอกสารเพิ่มเติม.xlsx")
check(
    "C07_sample_files_match_guide",
    (len(L), len(S), len(I)) == (3, 2, 0)
    and (len(L2), len(S2), sorted({i.source_row for i in I2})) == (2, 1, [4, 6, 7])
    and (len(L3), len(S3), len(I3)) == (0, 0, 0),
    f"ตัวอย่าง={len(L)}/{len(S)}/{len(I)} ฝึก rows={sorted({i.source_row for i in I2})}",
)

# C08: the guide contains every catalog text (whitespace-insensitive)
guide = "".join(read(ROOT / "USER_GUIDE.md").split())
missing = [
    m["id"] for m in cat["messages"] if "".join(m["message_th"].split()) not in guide
]
missing += [
    c_["id"]
    for c_ in cat["row_chips"] + cat["run_chips"]
    if "".join(c_["label_th"].split()) not in guide
]
check(
    "C08_guide_contains_all_catalog_statuses_and_messages",
    not missing,
    ", ".join(missing) or "ok",
)

# C09: forbidden-word check on the guide
rc = subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "check_guide_words.py")],
    capture_output=True,
    text=True,
)
check(
    "C09_guide_has_no_forbidden_words",
    rc.returncode == 0,
    rc.stdout.strip().splitlines()[-1],
)

# C10: definition example mirrors A2 headers / statuses / rule messages
import yaml  # noqa: E402

d = yaml.safe_load(
    read(ROOT / "examples" / "definitions" / "request_documents.v1.yaml")
)
tree = ast.parse(src["validation.py"])
obs = next(
    ast.literal_eval(n.value)
    for n in tree.body
    if isinstance(n, ast.Assign)
    and getattr(n.targets[0], "id", "") == "OBSERVED_STATUSES"
)
ids = {m["id"] for m in cat["messages"]}
msgs = (
    [r["message"] for r in d["rules"]]
    + [x["message"] for x in d["output"]["checks_after_render"]]
    + [d["duplicates"]["message"]]
)
check(
    "C10_definition_example_consistent_with_a2",
    tuple(d["source"]["columns"]) == tuple(HEADERS)
    and set(next(f["values"] for f in d["fields"] if f["id"] == "claim_status"))
    == set(obs)
    and all(m in ids for m in msgs),
    "columns/statuses/messages",
)

# C11: A3 ANSWER never says the platform exists / audit core exists
ans = read(ROOT / "ANSWER.md") if (ROOT / "ANSWER.md").exists() else ""
banned = [
    p
    for p in ("audit core", "แกนตรวจสอบเดิม", "มีอยู่แล้วในระบบ A2 ตรวจสอบย้อนหลัง")
    if p in ans
]
check(
    "C11_answer_has_no_unsupported_audit_claim", not banned, ", ".join(banned) or "ok"
)

(ROOT / "docs" / "a2_a3_check_results.json").write_text(
    json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
)
print(
    f"\n{len(results['checks']) - fail}/{len(results['checks'])} checks passed; {len(results['probes'])} probes recorded"
)
sys.exit(1 if fail else 0)
