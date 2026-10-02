"""Fail if USER_GUIDE.md contains words the guide must not use.

Forbidden (case-insensitive, whole words/phrases): JSON, API, schema,
placeholder, deploy, endpoint, batch, batch ID, row number, approver,
error report, xlsx.

Also checks that image file names in links do not contain them, and that
the term "Mail Merge" appears exactly once (compare once, at the start).

Run: python3 scripts/check_guide_words.py [path-to-guide.md]
Exit code 0 = pass, 1 = fail.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN = [
    "JSON",
    "API",
    "schema",
    "placeholder",
    "deploy",
    "endpoint",
    "batch ID",
    "batch",
    "row number",
    "approver",
    "error report",
    "xlsx",
]


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "USER_GUIDE.md"
    text = path.read_text(encoding="utf-8")
    failures = []
    for word in FORBIDDEN:
        # "batches", "APIs" etc. also count: match the word as a prefix of a Latin-letter run
        pattern = re.compile(
            rf"(?<![A-Za-z0-9]){re.escape(word)}[A-Za-z]*", re.IGNORECASE
        )
        for m in pattern.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            failures.append(
                f"{path.name}:{line}: forbidden word '{m.group(0)}' (rule: {word})"
            )
    merges = len(re.findall(r"Mail Merge", text))
    if merges != 1:
        failures.append(
            f"{path.name}: 'Mail Merge' appears {merges} times, expected exactly 1"
        )
    for f in failures:
        print("FAIL", f)
    print(
        f"checked {path} -> {'FAIL' if failures else 'PASS'} ({len(failures)} problem(s))"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
