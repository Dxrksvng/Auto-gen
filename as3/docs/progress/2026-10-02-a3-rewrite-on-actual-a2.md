# 2026-10-02 — เขียน A3 ใหม่ให้ต่อยอดจากโค้ด A2 ตามที่เป็นอยู่จริง

**What changed**
- เขียน `ANSWER.md` (3.1 ถึง 3.4) ใหม่เป็นภาษาไทย: ตาราง ใช้ซ้ำ / ต้องรื้อ / ยังไม่มี ผูก path:line ของ `as2/poc/`; เฟส 1 รองรับอะไรไม่รองรับอะไร; การออกแบบ; ข้อดีข้อเสียเฉพาะการออกแบบนี้พร้อมทางเลือกที่ไม่เลือก
- เพิ่มหลักฐานที่รันจริง: ทดสอบเรนเดอร์ภาษาไทย HTML->PDF (Chrome vs WeasyPrint, Sarabun vs Tahoma) และทดสอบเติมช่อง DOCX ด้วย docxtpl (`docs/rendering-test/`)
- ไดอะแกรม 2 ภาพ Mermaid->PNG (`docs/diagrams/`), Document Definition ตัวอย่าง 2 ไฟล์ (`examples/definitions/`), ไฟล์ Excel ตัวอย่าง 3 ไฟล์ (`examples/`), message catalog (`docs/message-catalog.json`)
- คู่มือผู้ใช้ `USER_GUIDE.md` + `USER_GUIDE.pdf`, mockup 10 หน้าจอ + ภาพ (`mockup/`, `docs/guide-images/`), แผนทดสอบการใช้งาน (`docs/usability-test-plan.md`, ไม่มีผล)
- สคริปต์ตรวจ: `scripts/check_guide_words.py`, `scripts/check_a2_a3.py` (รันโค้ด A2 จริง); เอกสารพิสูจน์ `docs/A2_A3_CONSISTENCY.md`
- แก้ข้อความเก่าในไฟล์ as3 เดิมที่อ้างว่า A2 มีอนุมัติ/ตรวจฟอนต์/audit (ASSUMPTIONS, GOVERNANCE, SPEC, DOCUMENT_DEFINITION) และใส่หมายเหตุในไฟล์อื่น

**Why**
- A3 ฉบับก่อนอ้างว่า A2 มี "แกนตรวจสอบ" (intake, preview, controlled release, audit) ซึ่งไม่มีในโค้ด A2
- คำสั่งงานให้ต่อยอด "A2 ที่แก้แล้ว" แต่ไม่พบ `as2/docs/A2_CHANGELOG.md` และ `as2/poc/*.py` ไม่ถูกแก้ตั้งแต่ 1 ต.ค. จึงยึดโค้ดตามที่เป็นอยู่ และทำสคริปต์ให้รันซ้ำได้เมื่อ A2 ถูกแก้

**What's affected**
- ไม่ได้แก้อะไรใน `as2/` (ไม่มีไฟล์ใหม่ใน as2/poc นอกจาก `__pycache__` จากการรัน)
- ส่วน A3 ในไฟล์รวม `Assignment_2_to_4.pdf` ตอนนี้สั้นและเก่ากว่า `as3/ANSWER.md` มาก ยังไม่ได้สร้าง PDF รวมใหม่

**ข้อค้นพบที่ควรรู้**
- WeasyPrint 68.1: ภาพถูกแต่ข้อความใน PDF เพี้ยน (ทดสอบแล้ว) ส่วน Chrome ถูกทั้งภาพและข้อความ
- docxtpl: สะกดชื่อช่องผิดแล้วช่องหายเงียบ ๆ และ `{% if %}` ถูกรันจริง ต้องมีตัวสแกนช่องของระบบเอง
- A2 โค้ด: คำนำหน้าซ้ำ, ไม่ escape, รันซ้ำเขียนทับ, แถวซ้ำสร้างสองฉบับ ขัดกับข้อความใน `as2/ANSWER.md` (ตรวจด้วย `check_a2_a3.py` P10, P11, P16, P18, P19)

**What's next**
1. ตัดสินใจติดตั้ง LibreOffice (Homebrew cask) เพื่อทดสอบ DOCX->PDF ภาษาไทย (ยังไม่ได้ติดตั้ง ต้องได้รับอนุมัติ)
2. แก้ A2 ตามรายการในตาราง 3.1 ข./ค. แล้วรัน `scripts/check_a2_a3.py` ซ้ำ
3. ทดสอบการใช้งานกับ 3 ถึง 5 คน ตามแผน
4. สร้าง `Assignment_2_to_4.pdf` ใหม่หลัง A2 A3 A4 นิ่ง
5. ตอบข้อ [TO CONFIRM] ท้าย `ANSWER.md`
