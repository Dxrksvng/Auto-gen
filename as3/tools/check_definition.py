"""Check the proposed Document Definition files against the REAL Assignment 2 code.

Usage: python3 tools/check_definition.py definitions/additional_document_request.v1.yaml
Exit code 0 = all checks passed, 1 = at least one failed. Read-only use of as2/.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / "as2" / "poc"))
from validation import HEADERS, OBSERVED_STATUSES  # noqa: E402  (the real A2 constants)

RULE_TYPES = {"required", "enum", "date_valid", "date_order", "list_of_text", "list_nonempty_when", "group_consistent"}
TRANSFORM_OPS = {"strip_leading", "map_names", "format_date"}
FORBIDDEN_KEYS = {"python", "script", "eval", "exec", "sql", "shell", "url", "http", "webhook", "javascript"}


def walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield path + "/" + str(k), k, v
            yield from walk(v, path + "/" + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")


def main(path: Path) -> int:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    results: list[tuple[bool, str]] = []
    add = lambda ok, msg: results.append((bool(ok), msg))

    # no executable / external constructs anywhere in the file
    bad = [p for p, k, _ in walk(data) if str(k).lower() in FORBIDDEN_KEYS]
    add(not bad, f"no forbidden keys (script/sql/http/...): {bad or 'none'}")

    if "columns" in (data.get("source") or {}) and data.get("phase_supported") != "none":
        cols = [c["column"] for c in data["source"]["columns"]]
        add(tuple(cols) == HEADERS, f"columns equal A2 HEADERS in order: {cols == list(HEADERS)}")
        status = next(c for c in data["source"]["columns"] if c["column"] == "claim_status")
        add(set(status["values"]) == OBSERVED_STATUSES, f"status values equal A2 OBSERVED_STATUSES: {sorted(status['values'])}")
        fields = {c["field"] for c in data["source"]["columns"]}
        used = set(data["template"]["fields_used"])
        add(used <= fields, f"template fields_used exist in the field list; unknown: {sorted(used - fields)}")
        a2_source = (ROOT.parent / "as2" / "poc" / "validation.py").read_text(encoding="utf-8")
        for rule in data["rules"]:
            add(rule["type"] in RULE_TYPES, f"rule type in closed set: {rule['type']}")
            add(f'"{rule["code"]}"' in a2_source, f"rule code {rule['code']} appears in as2/poc/validation.py")
        for t in data["transforms"]:
            add(t["op"] in TRANSFORM_OPS, f"transform op in closed set: {t['op']}")
    else:
        for rule in data.get("rules", []):
            add(rule["type"] in RULE_TYPES, f"(sketch) rule type in closed set: {rule['type']}")
        add(bool(data.get("needs_beyond_phase1")), "(sketch) lists what phase 1 does not support")

    n_confirm = len(re.findall(r"\[TO CONFIRM", path.read_text(encoding="utf-8")))
    for ok, msg in results:
        print(("PASS " if ok else "FAIL ") + msg)
    print(f"[TO CONFIRM] markers in file: {n_confirm}")
    return 0 if all(ok for ok, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
