# A2 CHANGELOG — แก้ A2 ตามผลตรวจเข้ม

**วันที่:** 2 ตุลาคม 2569 · **ฐานก่อนแก้:** commit `be601ad` (สถานะเดิม) · ทุกการแก้เป็น commit แยก (Conventional Commits) ยังไม่ได้ push
**วิธีทำ:** เขียน test ที่ล้มก่อน (เห็นผลล้มจริงก่อนแก้ทุกข้อ ยกเว้นที่ระบุ) แล้วแก้ให้ผ่าน
**สภาพแวดล้อมที่รัน:** macOS, Python 3.13.9, Chrome 154.0.8037.95, PyMuPDF 1.28.2, openpyxl 3.1.5, PyYAML 6.0.3 (ปักเวอร์ชันใน `poc/requirements.txt`)

## ผลรวมที่ตรวจแล้ว

| รายการ | ผล |
| --- | --- |
| `pytest -q` ใน venv สะอาดที่สร้างจาก `requirements-dev.txt` เท่านั้น | **133 ผ่าน** ใช้เวลา 26 วินาที (รวม test ที่เรียก Chrome จริง) |
| `ruff check .` | ผ่าน (ชุดกฎอยู่ใน `poc/ruff.toml`) |
| รัน pipeline กับ `data/Example claim table.xlsx` | 10 แถว → **สร้างจดหมาย 5 ฉบับ** ข้าม 5 ต้องแก้ไข 0 ซ้ำ 0 ไม่สำเร็จ 0 · กระทบยอดผ่าน · จำนวนแถว `REQUEST_DOC` ในไฟล์ = 5 ตรงกับจำนวนจดหมาย |
| ตรวจ PDF ทุกฉบับ | `verify_pdf` ผ่านทั้ง 5 และ test ตรวจซ้ำอิสระ (`test_sample_workbook_generates_one_verified_letter_per_request_row`) |
| ตรวจภาพด้วยตา | เปิดดูจดหมายครบทั้ง 5 ฉบับจากโค้ดฉบับสุดท้าย และซูมดู 1 ฉบับ (แถว 8, 220 dpi) |
| โปรเซส Chrome ตกค้างหลังรัน test | 0 |

## รายการแก้ไข

| ข้อ | สิ่งที่แก้ | ไฟล์ | test (ชื่อ) | ก่อน → หลัง |
| --- | --- | --- | --- | --- |
| A1 | คำนำหน้าซ้ำ: เก็บ "คุณ" ที่มีอยู่ ไม่เติมซ้ำ ไม่เติมให้ชื่อที่มีคำนำหน้าอื่น ชื่อรูปแบบแปลกคงเดิมและเตือน | `normalize.py` (`format_salutation`), `templates/`, `letter.py` · commit `fix(letter): render exactly one honorific…` | `tests/test_salutation.py`: `test_name_already_starting_with_khun_is_kept`, `test_plain_name_gets_khun_prefix`, `test_known_titles_do_not_get_khun[...]`, `test_unknown_format_is_kept_as_is_with_warning[...]` | `เรียน คุณ คุณสมชาย ใจดี` → `เรียน คุณสมชาย ใจดี` |
| A1 (ต่อ) | ชื่อภาษาอังกฤษต้องมีช่องว่างหลัง "คุณ" | `normalize.py` · commit `fix(letter): put a space between คุณ and a Latin-script name` | `test_latin_name_gets_khun_with_a_space`, `test_thai_name_gets_khun_without_a_space` | `คุณJohn Smith` → `คุณ John Smith` |
| A2 | ชื่อโรงพยาบาลไม่ซ้ำคำ | `normalize.py` (`hospital`) · commit `fix(letter): never repeat the hospital facility word` | `tests/test_hospital.py`: `test_known_prefix_is_kept[...]`, `test_bare_name_gets_hospital_prefix`, `test_never_doubles_the_word` | `โรงพยาบาล โรงพยาบาลกรุงเทพ` → `จากทางโรงพยาบาลกรุงเทพ` · คำถามเรื่องกติกาอื่นอยู่ใน `OPEN_QUESTIONS.md` ข้อ 12 |
| A3 | วันที่ พ.ศ. และอ่านวันที่หลายแบบ (วันที่จริง, ISO, dd/mm/yyyy, เลข serial Excel) ไม่ crash ปฏิเสธวันสิ้นสุดก่อนวันเริ่มพร้อมรหัส | `normalize.py` (`th_date`, `parse_date`), `validation.py` · commit `feat(dates): …` และ `feat(validation): …` | `tests/test_dates.py` (23 รายการ), `tests/test_validation.py::test_end_before_start_has_a_clear_code_and_thai_message`, `::test_start_date_accepts_strings_and_excel_serials[...]`, `tests/test_classification.py::test_excel_serial_number_dates_are_converted` | `01/01/2026` → `1 มกราคม 2569` · เลข serial `46023` → `1 มกราคม 2569` · วันที่ผิดลำดับ → `DATE_ORDER` พร้อมข้อความไทย |
| A4 | ตารางชื่อเอกสารที่อนุมัติ ชื่อไม่รู้จักกันทั้งแถว ห้ามพิมพ์อังกฤษดิบ | `config/document_names.yml`, `normalize.py` (`load_document_names`), `validation.py` · commit `feat(documents): …` | `tests/test_document_names.py` (7 รายการ), `tests/test_validation.py::test_unknown_document_name_is_an_error_naming_the_document`, `tests/test_batch.py::test_unknown_document_row_goes_to_rejected_report_without_a_pdf` | `1. Medical Report` → `1. รายงานทางการแพทย์` · `Discharge Summary` → แถวถูกกัน `UNKNOWN_DOCUMENT` |
| A5 | แถวที่สถานะไม่ใช่ `REQUEST_DOC` แต่มีรายการเอกสาร ต้องข้ามและแจ้ง | `validation.py` · commit `feat(validation): classify rows…` | `tests/test_classification.py::test_status_other_than_request_with_documents_is_a_listed_conflict`, `tests/test_batch.py::test_duplicate_and_conflict_rows_are_reported_not_silent` | `APPROVED` + `["x"]` ถูกข้ามเงียบ → ขึ้น `CONFLICTING_ROW` "ข้อมูลขัดแย้ง ตรวจสอบ" |
| A6 | แถวซ้ำสร้างฉบับเดียวและรายงานทั้งสองแถว รันซ้ำไม่เขียนทับ โฟลเดอร์ `run_<เวลา>_<แฮช 8>` และ manifest | `validation.py`, `generate_letters.py` · commit `feat(pipeline): …` | `tests/test_classification.py::test_duplicate_policy_and_documents_generates_one_and_reports_both_rows`, `::test_duplicate_detection_ignores_document_order`, `tests/test_batch.py::test_rerun_never_overwrites_previous_output`, `::test_two_runs_in_the_same_second_get_distinct_directories`, `::test_run_directory_name_has_timestamp_and_file_hash` | แถวเหมือนกัน 2 แถวสร้าง 2 ฉบับ → 1 ฉบับ + รายงาน · รันซ้ำใช้โฟลเดอร์ `batch_<แฮช>` เดิมและเขียนทับ → โฟลเดอร์ใหม่ทุกรอบ |
| A7 | ตรวจข้อความใน PDF กับ "บรรทัดที่ควรเป็น" ไม่ใช่ "ค่าอยู่ในข้อความ" ตรวจข้อความซ้ำ ตัวค้าง `{{ < >` วันที่รูปแบบผิด จำนวนข้อ แบนเนอร์ผิดโหมด ฟอนต์ที่ฝัง | `verify.py`, `letter.py` · commit `feat(verify): …` | `tests/test_verify.py`: `test_known_defects_are_reported[...]` (5 ข้อบกพร่อง), `test_wrong_number_of_numbered_items_is_reported`, `test_wrapping_and_whitespace_differences_do_not_matter`, `test_decomposed_sara_am_from_the_extractor_still_matches`, `test_long_wrapped_document_name_does_not_fail_a_correct_pdf`, `test_verifier_catches_a_pdf_that_does_not_match_the_row` | ชื่อเอกสารยาวราว 390 ตัวอักษรที่ตัดบรรทัดทำให้ verify ล้มทั้งที่ PDF ถูก (ทดสอบก่อนแก้ ตอนสำรวจ) → ผ่าน (แก้ที่ตัวตรวจ ไม่ใช่ข้อมูล) |
| A8 | ฟอนต์ที่แพ็กมา (Sarabun, SIL OFL 1.1 + ไฟล์ไลเซนส์) โหลดด้วย path สัมพัทธ์ ไม่มี path ของ macOS | `assets/fonts/`, `renderer.py` · commit `feat(render): …` | `tests/test_renderer.py::test_bundled_thai_font_and_its_license_are_present`, `::test_no_platform_specific_font_paths_in_source`, `::test_render_creates_one_page_pdf_with_embedded_sarabun_and_logo` | `FONT_CANDIDATES = (/System/Library/Fonts/Supplemental/Tahoma.ttf, …)` → `assets/fonts/Sarabun-*.ttf` · เปลี่ยนจาก ReportLab เป็น HTML + Chrome |
| A8 (ผลดูภาพ) | **ข้อบกพร่อง 2 อย่างที่ test ข้อความมองไม่เห็น พบจากการดูภาพจดหมาย:** (1) โลโก้เป็นกล่องดำ (ดึงภาพจาก PDF โดยไม่มี soft mask) (2) ชื่อ "โรงพยาบาลเมดพาร์ค" ถูกตัดเป็น "เมดพาร์" / "ค" คนละบรรทัด | `scripts/extract_logo.py`, `assets/logo.png`, `renderer.py`, `templates/request_letter_th.html` · commit `fix(render): fix logo background and mid-word line breaks…` | `tests/test_renderer.py::test_logo_keeps_its_transparent_background`, `::test_hospital_and_policy_number_are_wrapped_in_a_no_break_span`, `::test_hospital_name_is_never_split_across_lines` (ทำซ้ำข้อบกพร่องได้ก่อนแก้) | โลโก้กล่องดำ → โปร่งใส · `โรงพยาบาลเมดพาร์` / `ค` → `โรงพยาบาลเมดพาร์ค` บรรทัดเดียว · ชื่อ เลขกรมธรรม์ และวันที่ไม่ถูกตัดกลาง |
| A9 | จดหมายตาม template ของโจทย์: โลโก้ ชื่อบริษัท ประโยคแอป ช่องทางติดต่อ ท้ายจดหมาย แก้ "ท่าสามารถ" เป็น "ท่านสามารถ" (ระบุ TO CONFIRM) ลบแบนเนอร์ "ห้ามส่งลูกค้า" ออกจากผลปกติ ให้มีเฉพาะ `--preview` | `config/letter.yml`, `letter.py`, `templates/`, `renderer.py` | `tests/test_renderer.py::test_html_contains_template_blocks_in_order`, `::test_banner_only_in_preview_mode`, `::test_preview_pdf_carries_the_banner`, `::test_template_config_corrects_the_known_typo`, `tests/test_batch.py::test_preview_mode_is_marked_in_directory_manifest_and_pdf` | ข้อความตัวอย่างย่อ + แบนเนอร์ "ห้ามส่งลูกค้า" ทุกฉบับ → ตาม template (ดู `docs/img/letter_sample_row04.png`) |
| A10 | ปักเวอร์ชัน README 5 นาที ruff ตัวอย่างข้อมูลหลายปัญหา | `poc/requirements*.txt`, `poc/README.md`, `poc/ruff.toml`, `scripts/make_demo_workbook.py` · commits `chore: add explicit ruff rule set`, `build: pin dependencies…` | `tests/test_demo_workbook.py` (**ไม่ได้เขียนให้ล้มก่อน**: เขียนหลังโค้ด เพื่อกันตัวอย่างในเอกสารล้าสมัย) | ไม่มี requirements → ปักเวอร์ชัน ยืนยันใน venv สะอาด |
| (เพิ่ม) | Chrome 154 เขียน PDF แล้วไม่ปิดตัวเอง (ทำให้ test ค้างครั้งแรก) | `renderer.py` (`render_letter` รอ PDF ครบแล้วสั่งปิดกลุ่มโปรเซส) | ทุก test ที่สร้าง PDF · ตรวจว่าไม่มีโปรเซสตกค้าง | ค้างจนหมดเวลา → จบใน ~1 วินาทีต่อฉบับ |

## ทางเลือกที่ลองและไม่เลือก (มีหลักฐาน)

| ทางเลือก | ผลที่ทดสอบ | ตัดสินใจ |
| --- | --- | --- |
| WeasyPrint 68.1 สร้าง PDF | ภาพถูก แต่ข้อความใน PDF เพี้ยน ("น้ำ" กลายเป็น "น˺้ำ") ทำให้ตรวจข้อความไม่ได้ | ไม่ใช้ |
| ReportLab (เดิม) | **ไม่ได้ทดสอบการตัดคำภาษาไทยของมันในเซสชันนี้** ปัญหาที่พบจริงในโค้ดเดิมคือ path ฟอนต์ที่ใช้ได้เฉพาะ macOS และข้อมูลที่มี `<...>` ถูกกลืนเพราะไม่ escape | เปลี่ยนเป็น HTML + Chrome (ตัดคำด้วยพจนานุกรมของ Chrome ซึ่งยังตัดชื่อเฉพาะผิดได้ จึงมีการกันตัดบรรทัดในชื่อ/เลข/วันที่) |
| ตัวดึงข้อความ: pdfplumber | สลับลำดับวรรณยุกต์ (`ย่อ` → `ยอ่`) | ไม่ใช้ |
| ตัวดึงข้อความ: pypdf | วรรณยุกต์กลายเป็นอักขระว่าง | ไม่ใช้ |
| ตัวดึงข้อความ: pdfium | ตัวอักษรซ้ำและสลับ | ไม่ใช้ |
| ตัวดึงข้อความ: **PyMuPDF** | ถูกต้องกับ PDF จาก Chrome | **ใช้** ไลเซนส์ AGPL ต้องให้ฝ่ายที่เกี่ยวข้องพิจารณา (`OPEN_QUESTIONS.md` ข้อ 21) |

ผลดิบอยู่ที่ `../as3/docs/rendering-test/` (ทดสอบ 2 ต.ค. 2569) และการทดสอบ pdfplumber/pypdf/pdfium ทำในเซสชันนี้ด้วยแผ่นทดสอบเดียวกัน (ไม่ได้เก็บสคริปต์ไว้ในโปรเจกต์นี้)

## ตรวจแล้ว และไม่ได้ตรวจ

**ตรวจแล้ว**

- ชุดทดสอบทั้งหมด 133 ข้อ และ ruff ใน venv ที่สร้างใหม่จาก requirements ที่ปักเวอร์ชัน (ไม่พึ่ง venv เดิม)
- เห็น test ล้มก่อนแก้ในข้อ A1, A2, A3, A4, validation (A3/A4/A5/A6), renderer/verify, pipeline, โลโก้, การตัดบรรทัด, วันที่ไม่ตัด, ชื่อละตินมีช่องว่าง
- pipeline จริงด้วยคำสั่ง `python generate_letters.py` กับไฟล์ของโจทย์ และกับไฟล์ตัวอย่างหลายปัญหา (ได้ 3 ฉบับ ข้าม 2 ต้องแก้ 3 ซ้ำ 1 กระทบยอดผ่าน)
- ดูภาพจดหมายครบ 5 ฉบับจากโค้ดฉบับสุดท้าย (แถว 2, 8, 10 ที่ 80 dpi แถว 4 และ 6 ที่ 110 dpi) และซูมแถว 8 ที่ 220 dpi: วรรณยุกต์และสระซ้อนอยู่ตำแหน่งถูก ชื่อโรงพยาบาลไม่ถูกตัด โลโก้โปร่งใส
- ไม่มีโปรเซส Chrome ตกค้างหลัง test และหลังรัน CLI

**ไม่ได้ตรวจ**

- **Linux และ Python เวอร์ชันอื่นนอกจาก 3.13.9** (ไม่มี Docker ในเครื่อง) และ Chrome เวอร์ชันอื่น
- **ตำแหน่งวรรณยุกต์ด้วยโปรแกรม** ทำไม่ได้จากข้อความ จึงยังไม่มีภาพอ้างอิงเทียบอัตโนมัติ (golden image) เมื่อเปลี่ยน Chrome หรือฟอนต์ต้องดูภาพซ้ำ
- ไฟล์ใหญ่ ไฟล์ `.xls` `.csv` และ Excel ที่ใช้ระบบวันที่ 1904
- ไฟล์ template ต้นฉบับ (.docx) และไฟล์ Excel บน Google Drive ของโจทย์ ไม่มีในมือ ใช้เฉพาะ `data/template_test.pdf` และ `data/Example claim table.xlsx` ที่มีอยู่
- ถ้อยคำ ชื่อบริษัท คำแปลชื่อเอกสาร กติกาคำนำหน้า ข้อกำหนดทางกฎหมาย ระยะเวลาเก็บ ล้วนยังไม่ได้ยืนยัน (`OPEN_QUESTIONS.md`)
- ไลเซนส์ของฟอนต์ Sarabun และโลโก้สำหรับการใช้กับลูกค้าจริง (ฟอนต์: OFL 1.1 ตามไฟล์ที่แนบ ไม่ได้ให้ฝ่ายกฎหมายตรวจ)

## ผลกระทบต่อ A3 (ยังไม่ได้แก้ A3)

`as3/` ไม่ได้ถูกแก้ในงานนี้ A3 ฉบับที่เขียนไว้ก่อนหน้าอ้างอิง A2 **ฉบับเก่า** ข้อความต่อไปนี้ใน `as3/ANSWER.md` และ `as3/docs/A2_A3_CONSISTENCY.md` ล้าสมัย และตัวตรวจ `as3/scripts/check_a2_a3.py` ล้มทันทีเพราะหา pattern เก่าในโค้ดไม่เจอ (รันแล้วเมื่อ 2 ต.ค. 2569):

- ตาราง "ต้องรื้อ": คำนำหน้าซ้ำ, "โรงพยาบาล" ซ้ำ, ไม่ escape, วันที่ ค.ศ., ฟอนต์ macOS เท่านั้น, ไม่มี requirements, ตรวจ PDF ไม่ครบ, รันซ้ำเขียนทับ, แถวซ้ำสร้างสองฉบับ, สถานะขัดแย้งถูกข้ามเงียบ ล้วนแก้แล้วใน A2 นี้
- เลขบรรทัด A2 ที่ A3 อ้าง (`validation.py:26-72` ฯลฯ) ไม่ตรงอีกแล้ว
- ไฟล์ `docs/A2_CHANGELOG.md` ที่ A3 ใช้ยืนยันว่า "A2 แก้แล้ว" ตอนนี้มีอยู่ (ไฟล์นี้)
- ที่ **ยังไม่มีใน A2** ตามที่ A3 ระบุ และยังเป็นจริง: บันทึกตรวจสอบ (audit log), การอนุมัติ, การควบคุมสิทธิ์, ทะเบียนแบบฟอร์ม, หน้าอัปโหลด, การตรวจแถวซ้ำข้ามรอบ

ควรรัน A3 ใหม่หลังตัดสินใจเรื่อง A2 นี้ และปรับตัวตรวจให้ตรงกับโค้ดใหม่
