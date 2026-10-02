"""Fail if the Thai user guide contains words non-technical staff should not see.

Scans the text a reader sees: Markdown link targets, image paths and HTML comments are removed first.
Latin words use word boundaries (so 'capital' does not match 'api'). Exit 1 if any hit.
Usage: python3 tools/check_guide_words.py USER_GUIDE.md [more files]
"""
import re
import sys
from pathlib import Path

FORBIDDEN = ["JSON", "API", "schema", "placeholder", "deploy", "endpoint", "batch", "batch ID",
             "row number", "approver", "error report", "xlsx"]


def visible_text(md: str) -> str:
    md = re.sub(r"<!--.*?-->", " ", md, flags=re.S)
    md = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", md)       # image: keep alt text, drop path
    md = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", md)        # link: keep label, drop target
    return md


def main(paths: list[str]) -> int:
    bad = 0
    for p in paths:
        text = visible_text(Path(p).read_text(encoding="utf-8"))
        for word in FORBIDDEN:
            for m in re.finditer(r"(?<![A-Za-z])" + re.escape(word) + r"(?![A-Za-z])", text, flags=re.I):
                line = text.count("\n", 0, m.start()) + 1
                print(f"FOUND {word!r} in {p} (visible-text line {line}): ...{text[max(m.start()-25, 0):m.end()+25]!r}")
                bad += 1
    print("RESULT:", "FAIL" if bad else "PASS", f"({bad} hits, {len(FORBIDDEN)} words checked)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
