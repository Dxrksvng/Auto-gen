"""Upload-time field check (PROPOSAL, small working sketch).

For a template (.docx or .html) and a Document Definition, report:
  - fields written in the template that the definition does not have      (unknown)
  - fields the definition requires but the template never uses            (missing)
  - broken braces such as {{ชื่อ or ชื่อ}}                                  (malformed)
For .docx the text of each paragraph is joined first, because Word can split one field across several runs.

Usage: python3 tools/check_template_fields.py templates/x.docx definitions/y.yaml
"""
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import yaml

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def template_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        with zipfile.ZipFile(path) as z:
            root = ET.fromstring(z.read("word/document.xml"))
        return "\n".join("".join(t.text or "" for t in p.iter(W + "t")) for p in root.iter(W + "p"))
    return path.read_text(encoding="utf-8")


def main(template: Path, definition: Path) -> int:
    d = yaml.safe_load(definition.read_text(encoding="utf-8"))
    allowed = {c["field"] for c in d["source"]["columns"]}
    required_in_template = set(d["template"]["fields_used"])
    text = template_text(template)
    used = set(re.findall(r"\{\{([^{}]+)\}\}", text))
    stripped = re.sub(r"\{\{[^{}]*\}\}", "", text)
    malformed = len(re.findall(r"\{\{|\}\}", stripped))
    unknown = sorted(used - allowed)
    missing = sorted(required_in_template - used)
    print(f"template: {template.name}  fields found: {len(used)}")
    print(f"  unknown fields : {unknown or 'none'}")
    print(f"  missing fields : {missing or 'none'}")
    print(f"  broken braces  : {malformed}")
    ok = not unknown and not missing and malformed == 0
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
