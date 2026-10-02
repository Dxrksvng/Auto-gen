"""Hand-build two minimal .docx files (no python-docx) to exercise check_template_fields.py.
Not verified to open in Microsoft Word; structure follows the minimal WordprocessingML package."""
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "templates"

def build(name, paragraphs, split_field_in_runs=False):
    body = []
    for i, text in enumerate(paragraphs):
        if split_field_in_runs and i == 0:
            # simulate Word splitting one field over several runs: "{{ชื่อ" + "ลูกค้า}}"
            body.append('<w:p><w:r><w:t xml:space="preserve">เรียน คุณ {{ชื่อ</w:t></w:r><w:r><w:t>ลูกค้า}}</w:t></w:r></w:p>')
        else:
            body.append(f'<w:p><w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>')
    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
           + "".join(body) + "</w:body></w:document>")
    ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
    with zipfile.ZipFile(OUT / name, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct); z.writestr("_rels/.rels", rels); z.writestr("word/document.xml", doc)
    print("wrote", OUT / name)

good = ["เรียน คุณ {{ชื่อลูกค้า}}", "กรมธรรม์เลขที่ {{เลขกรมธรรม์}} ความคุ้มครอง {{วันเริ่มคุ้มครอง}} ถึง {{วันสิ้นสุดคุ้มครอง}}",
        "จากทางโรงพยาบาล{{ชื่อโรงพยาบาล}} ขอเอกสารดังนี้", "{{รายการเอกสาร}}"]
build("additional_document_request_v1.docx", good, split_field_in_runs=True)
bad = ["เรียน คุณ {{ชื่อลูกค้าา}}", "กรมธรรม์เลขที่ {{เลขกรมธรรม์}} ความคุ้มครอง {{วันเริ่มคุ้มครอง}} ถึง {{วันสิ้นสุดคุ้มครอง}}",
       "จากทางโรงพยาบาล{{ชื่อโรงพยาบาล ขอเอกสารดังนี้", "{{รายการเอกสาร}}"]
build("fixture_bad_fields.docx", bad)
