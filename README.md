<div align="center">

# Auto-gen

**Spreadsheet in, reviewed PDF letters out: a document-automation workflow with validation and audit.**

![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Input Excel (.xlsx)](https://img.shields.io/badge/Input-Excel_(.xlsx)-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white) ![Output Thai PDF letters](https://img.shields.io/badge/Output-Thai_PDF_letters-EF4444?style=for-the-badge) ![LLM none in the POC](https://img.shields.io/badge/LLM-none_in_the_POC-lightgrey?style=for-the-badge)

</div>

> The tool does not send letters to customers. It produces files for a human to review and release.

## Tech stack

<p align="center">
  <img src="https://skillicons.dev/icons?i=py,html,chrome,github&perline=10" alt="Tech stack" />
</p>

## Workflow

```mermaid
flowchart LR
    U["Business user"] --> I["File intake"]
    I --> V["File, schema and row validation"]
    V --> X["Actionable exception report"]
    V --> N["Normalized records"]
    N --> B["Confirmed business rules\n(REQUEST_DOC rows only)"]
    B --> L["LetterData"]
    T["Approved versioned template"] --> R["PDF renderer\nHeadless Chrome"]
    L --> R
    R --> Q["Output checks\nPDF text vs expected text"]
    Q --> H["Preview and review"]
    H --> D["Controlled release boundary"]
    I -.-> M[("Batch manifest,\nidentity and audit")]
    Q -.-> M
```

## Quick start

```bash
cd poc
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python generate_letters.py "../data/Example claim table.xlsx"
```

Needs Python 3.13 and Chrome or Chromium (used to render HTML to PDF). See [`poc/README.md`](poc/README.md) for the expected output and details, and [`SPEC.md`](SPEC.md), [`ARCHITECTURE.md`](ARCHITECTURE.md), [`FAILURE_MODES.md`](FAILURE_MODES.md) for design notes.

---

