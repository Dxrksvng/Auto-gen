# การทดสอบการเรนเดอร์ภาษาไทย และการเติมช่องใน DOCX

**วันที่รัน:** 2 ตุลาคม 2569 เครื่องเดียว macOS ไม่ใช่ Linux
**ข้อควรระวัง:** ผลนี้ใช้ตัดสินได้เฉพาะสิ่งที่ทดสอบ อ่านขอบเขตก่อนอ้างอิง

## สิ่งที่ทดสอบ

| สคริปต์ | ทดสอบอะไร | ผลดิบ |
| --- | --- | --- |
| `run_thai_render_test.py` | แปลงแผ่นทดสอบภาษาไทย 6 กรณี จาก HTML เป็น PDF ด้วย WeasyPrint 68.1 และ Chrome 154.0.8037.92 (ไม่มีหน้าจอ) กับฟอนต์ Sarabun และ Tahoma แล้วดึงข้อความด้วย PyMuPDF 1.28.2 เทียบกับต้นฉบับ | `results.json`, `out/*.pdf`, `out/*.png` |
| `docx_field_test.py` | การเติมช่อง `{{ชื่อภาษาไทย}}` ลงไฟล์ DOCX ด้วย docxtpl 0.20.2 กับ Jinja2 3.1.6 (6 กรณี: ปกติ ช่องที่แบ่งเป็นหลายส่วน สะกดผิด เว้นวรรคในชื่อช่อง คำสั่งเงื่อนไข) **ไม่ได้ทดสอบการแปลงเป็น PDF** | `docx_field_results.json`, `out/*.docx` |

## ผลสรุป

- ภาพของทั้ง 4 ชุด (2 ฟอนต์ x 2 เครื่องมือ) ถูกต้อง ผมดูภาพเอง ตัดบรรทัดตามขอบเขตคำ วรรณยุกต์และสระซ้อนอยู่ตำแหน่งถูก
- ข้อความที่ดึงจาก PDF: Chrome ตรงกับต้นฉบับทั้ง 6 กรณี WeasyPrint **ไม่ตรงทั้ง 6 กรณี** (เช่น "จากการ" กลายเป็น "จ้ำกก้ำร") แม้ภาพดูถูก
- การเติมช่อง DOCX: ชื่อภาษาไทยใช้ได้ สะกดผิดทำให้ช่องหายเงียบ ๆ เว้นวรรคในชื่อช่องทำให้เกิดข้อผิดพลาดของไลบรารี และ `{% if %}` ถูกรันจริง

## ไม่ได้ทดสอบ

DOCX → PDF (ไม่มี LibreOffice ในเครื่อง) Linux ฟอนต์อื่นนอกจาก Sarabun และ Tahoma ปริมาณและความเร็ว ไฟล์ DOCX ที่สร้างจาก Word หรือ Google Docs จริง สิทธิ์ใช้ฟอนต์ Tahoma

## รันซ้ำ

```bash
cd as3/docs/rendering-test
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib \
  uv run --with weasyprint --with pymupdf python run_thai_render_test.py
uv run --with python-docx --with docxtpl python docx_field_test.py
```

- สคริปต์แรกดาวน์โหลดฟอนต์ Sarabun (ไลเซนส์ OFL) จาก `google/fonts` บน GitHub ไปไว้ที่ `.fonts/` ถ้ายังไม่มี และต้องมี Google Chrome ที่ `/Applications/Google Chrome.app`
- บนเครื่องที่ไม่ใช่ macOS ต้องแก้ path ของ Chrome และของฟอนต์ Tahoma (หรือตัดชุด Tahoma ออก)
- `DYLD_FALLBACK_LIBRARY_PATH` ชี้ไปยังไลบรารี pango ของ Homebrew ที่ WeasyPrint ต้องใช้
