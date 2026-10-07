# test ของ T-03: จองคิวสำเร็จ
# AC-BKG-01 (FR-BKG-04)
from app.db.models import Slot
from tests.conftest import AUTH


def test_AC_BKG_01(client, make_slot):
    """AC-BKG-01: ยืนยันตัวตนแล้ว และช่วง 09.00 น. มีที่นั่งว่าง จองแล้วต้องสำเร็จ"""
    slot = make_slot(start="09:00", remaining=1)

    res = client.post("/bookings", json={"slot_id": slot.id}, headers=AUTH)

    assert res.status_code == 201


def test_TC_BKG_01_1_booking_success(client, make_slot, db):
    """TC-BKG-01-1: ทางปกติ - จองสำเร็จแล้วต้องบันทึกและตัดที่นั่ง"""
    # Given: ยืนยันตัวตนแล้ว และช่วง 09.00 น. มีที่นั่งว่าง 1 ที่
    slot = make_slot(start="09:00", remaining=1)

    # When: ยืนยันการจอง
    res = client.post("/bookings", json={"slot_id": slot.id}, headers=AUTH)

    # Then: บันทึกสำเร็จ; แสดงหมายเลขคิว (รอ Q-02); ที่นั่งว่างของช่วงนั้นเป็น 0
    assert res.status_code == 201
    db.refresh(slot)
    assert slot.remaining == 0
    # รอ Q-02: ยังไม่ตรวจว่า response มีหมายเลขคิวหรือแสดงบนหน้าจออย่างไร


def test_TC_BKG_01_2_last_slot_booking(client, make_slot, db):
    """TC-BKG-01-2: ขอบ - slot สุดท้ายก่อนเต็มต้องยังสามารถจองได้และลดเป็น 0"""
    # Given: ยืนยันตัวตนแล้ว และช่วง 09.00 น. มีที่นั่งว่าง 1 ที่ เป็น slot สุดท้ายก่อนเต็ม
    slot = make_slot(start="09:00", remaining=1)

    # When: ยืนยันการจอง
    res = client.post("/bookings", json={"slot_id": slot.id}, headers=AUTH)

    # Then: บันทึกสำเร็จเป็นรายการสุดท้าย; แสดงหมายเลขคิว (รอ Q-02); ที่นั่งว่างของช่วงนั้นลดจาก 1 เป็น 0
    assert res.status_code == 201
    db.refresh(slot)
    assert slot.remaining == 0
    # รอ Q-02: ยังไม่ตรวจว่าแสดงหมายเลขคิวตามรูปแบบที่กำหนดหรือไม่


def test_TC_BKG_01_3_rejects_unverified_or_full_slot(client, make_slot, db):
    """TC-BKG-01-3: ทางผิด - ไม่ยืนยันตัวตนหรือ slot เต็มต้องปฏิเสธและไม่ลดที่นั่ง"""
    # Given: ยังไม่ได้ยืนยันตัวตน หรือช่วง 09.00 น. ไม่มีที่นั่งว่าง
    slot = make_slot(start="09:00", remaining=1)
    full_slot = make_slot(start="10:00", remaining=0, days_from_today=2)

    # When: พยายามยืนยันการจอง
    unauth_res = client.post("/bookings", json={"slot_id": slot.id})
    full_res = client.post("/bookings", json={"slot_id": full_slot.id}, headers=AUTH)

    # Then: ปฏิเสธการจองและไม่บันทึก; ไม่ลดจำนวนที่นั่ง; ข้อความ/หน้าจอแจ้งผล (spec ไม่ได้บอกชัดเจนว่าควรแสดงข้อความอะไรในกรณีนี้)
    assert unauth_res.status_code == 401
    assert full_res.status_code == 409
    db.refresh(slot)
    db.refresh(full_slot)
    assert slot.remaining == 1
    assert full_slot.remaining == 0
    # spec ไม่ได้กำหนดข้อความแจ้งผลแบบละเอียด จึงไม่ assert เนื้อหาข้อความ
