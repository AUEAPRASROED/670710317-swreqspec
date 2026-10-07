# RTM: จองคิวตรวจสุขภาพ (Booking)
สร้างด้วย /verify เมื่อ 2569-10-07 08:43 | test: backend 7 ผ่าน / frontend 1 ผ่าน

## สรุปผลตรวจ
- โค้ดที่ทำงานชัดเจน: POST /bookings เบื้องต้น, GET /slots เบื้องต้น, และ test backend/ frontend ผ่านในระดับที่มีอยู่
- มีข้อค้นพบที่ยังเป็นช่องโหว่สำคัญ: ขอบเขตวัน 30 วัน, PostgreSQL, audit log, และ Open Question Q-02
- ยังมี requirement หลายข้อที่ยังไม่ได้ถึงในโค้ด (FR-BKG-02, FR-BKG-03, FR-BKG-05, IF-HIS-01, IF-NOT-01 เป็นต้น)

## ตารางตามรอย (RTM)
| ID | AC | Task | โค้ดที่เกี่ยวข้อง | Test | สถานะ |
|---|---|---|---|---|---|
| FR-BKG-01 | AC-BKG-05 | T-02 | backend/app/slots/service.py::list_available_slots, backend/app/slots/router.py::get_slots | tests/test_AC_BKG_05.py::test_AC_BKG_05 | ช่องโหว่ |
| FR-BKG-02 | AC-BKG-02 | T-04 | ไม่มี logic ปฏิเสธคิวซ้ำใน backend/app/booking/service.py | ไม่มี | ยังไม่ถึง |
| FR-BKG-03 | AC-BKG-03 | T-05, T-11, T-12 | ไม่มี logic เสนอ 3 ช่วงที่ว่างใกล้เคียงและ no booking collision | ไม่มี | ยังไม่ถึง |
| FR-BKG-04 | AC-BKG-01 | T-03, T-06 | backend/app/booking/service.py::create_booking, backend/app/booking/router.py::create_booking | tests/test_AC_BKG_01.py::test_AC_BKG_01 และ 3 test ใหม่ | รอ Q-xx |
| FR-BKG-05 | AC-BKG-04 | T-07 | ไม่มี notify queue หรือ retry queue ใน backend/app | ไม่มี | ยังไม่ถึง |
| FR-BKG-06 | ไม่มี AC | T-02, T-10 | backend/app/slots/service.py::list_available_slots filters package_code | ไม่มี test ที่ตรวจ package change จริง | ครบ (backend) |
| NFR-PERF-01 | AC-BKG-05 | T-02 | backend/app/slots/service.py | tests/test_AC_BKG_05.py::test_AC_BKG_05 | ครบ |
| NFR-SEC-01 | ไม่มี AC | ไม่มี | ไม่มี TLS / HTTPS / security config ในโค้ด | ไม่มี | ยังไม่ถึง |
| NFR-REL-02 | AC-BKG-04 | T-07 | ไม่มี retry queue / resend logic ใน backend/app | ไม่มี | ยังไม่ถึง |
| NFR-USE-01 | ไม่มี AC | ไม่มี | ไม่มี usability validation / test | ไม่มี | ยังไม่ถึง |
| CON-TECH-01 | ไม่มี AC | T-01 | backend/app/config.py::DATABASE_URL, backend/app/db/session.py::engine | ไม่มี | ช่องโหว่ |
| DOM-PDPA-01 | AC-BKG-06 | T-01, T-08 | backend/app/db/models.py::AuditLog แต่ไม่มี write path ใน app | ไม่มี | ช่องโหว่ |
| IF-IDP-01 | ไม่มี AC ระบุตรง | T-03 | backend/app/auth/idp.py::get_verified_hn | อ implicit ผ่าน AC-BKG-01 | ครบ |
| IF-HIS-01 | ไม่มี AC | T-09 | ไม่มี HIS client หรือ lookup ใน backend/app | ไม่มี | ยังไม่ถึง |
| IF-NOT-01 | ไม่มี AC | T-07 | ไม่มี async notification queue / sender ใน backend/app | ไม่มี | ยังไม่ถึง |

## ข้อค้นพบ
### F-01: FR-BKG-01 ไม่ตรงกับ spec
- spec ระบุว่า “ภายใน 30 วันข้างหน้า” แต่โค้ดใน backend/app/slots/service.py ใช้ `DAYS_AHEAD = 14`
- จึงคืนช่วงเวลาเพียง 14 วัน ไม่ใช่ 30 วันตาม FR-BKG-01 และ AC-BKG-05/Traceability
- ผล: เป็นช่องโหว่ของ requirement กับโค้ด

### F-02: CON-TECH-01 ไม่ถูกบังคับจริง
- spec ระบุ “ใช้ฐานข้อมูล PostgreSQL ตามมาตรฐานฝ่าย IT”
- backend/app/config.py ตั้งค่าเริ่มต้นเป็น `sqlite:///./dev.db` และไม่บังคับ `DATABASE_URL` เป็น PostgreSQL
- ผล: โค้ดยังใช้ SQLite ใน environment เริ่มต้น จึงไม่สอดคล้องกับ constraint

### F-03: DOM-PDPA-01 มีตารางแต่ไม่มีการบันทึก audit log จริง
- backend/app/db/models.py มี `AuditLog` กับฟิลด์ actor_id, action, hn, accessed_at
- แต่ไม่มี middleware / function / endpoint ที่สร้าง AuditLog ระหว่าง access
- ผล: table ถูกสร้างแล้ว แต่ requirement “บันทึก audit log ทุกครั้งที่เข้าถึงข้อมูลสุขภาพ” ยังไม่เป็นจริง

### F-04: Q-02 ยังคงเป็น Open Question แต่โค้ดใช้การเดา
- spec ระบุ Q-02 ว่า “หมายเลขคิวรีเซ็ตรายวัน หรือนับต่อเนื่อง และมีรูปแบบอย่างไร?” ยังไม่ได้คำตอบ
- backend/app/booking/service.py::next_queue_no ใช้ format `A{count + 1:03d}` และเรียกใหม่ทุกวัน
- ผล: นี่คือการตัดสินใจแทนทีมและไม่ใช่ requirement ที่ได้รับการตอบรับจากผู้มีอำนาจ ดังนั้น FR-BKG-04 ยังอยู่ในสถานะ “รอ Q-xx”

## ข้อสรุปเชิงตรวจ
- Test ที่ผ่านในปัจจุบัน: backend 7/7, frontend 1/1
- แต่ verification ตาม spec ยังพบว่าความครบของ feature อยู่ที่ประมาณ 4/12 requirement หลัก (และ constraint/quality several items) เป็น “ครบ” หรือ “รอ Q-xx” อย่างไม่สมบูรณ์
- ดังนั้นผลสรุปขั้นสุดท้ายคือ feature นี้ยังไม่พร้อมยืนยันว่า “ตรงตาม spec” เนื่องจากมีข้อค้นพบข้างต้นและ requirement หลายรายการยังคง “ยังไม่ถึง”
