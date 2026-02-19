from sqlalchemy.orm import Session
from app.models.attendance_model import Attendance
from app.schemas.attendance_schema import AttendanceCreate
from fastapi import HTTPException

from sqlalchemy import func
from datetime import date, timedelta
from sqlalchemy import Integer


def get_weekly_attendance(db: Session):

    today = date.today()
    week_start = today - timedelta(days=6)

    records = (
        db.query(
            Attendance.date,
            func.count(Attendance.id).label("total"),
            func.sum(
                func.cast(Attendance.status == "present", Integer)
            ).label("present_count")
        )
        .filter(Attendance.date >= week_start, Attendance.date <= today)
        .group_by(Attendance.date)
        .order_by(Attendance.date)
        .all()
    )

    record_map = {
        r.date: {
            "total": r.total,
            "present": r.present_count or 0
        }
        for r in records
    }

    result = []

    for i in range(7):
        current_date = week_start + timedelta(days=i)

        total = record_map.get(current_date, {}).get("total", 0)
        present = record_map.get(current_date, {}).get("present", 0)

        pct = round((present / total) * 100) if total > 0 else 0

        result.append({
            "date": str(current_date),
            "day": current_date.strftime("%a"),
            "total": total,
            "present": present,
            "pct": pct
        })

    return {"success": True, "data": result}

def mark_attendance(data: AttendanceCreate, db: Session):
    existing = db.query(Attendance).filter(
        Attendance.user_id == data.user_id,
        Attendance.date == data.date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Attendance already marked for this date")

    record = Attendance(
        user_id=data.user_id,
        date=data.date,
        status=data.status
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"success": True, "message": "Attendance marked", "data": {"id": record.id}}

def get_attendance_by_user(user_id: int, db: Session):
    records = db.query(Attendance).filter(Attendance.user_id == user_id).all()
    return {"success": True, "data": records}

def get_all_attendance(db: Session):
    records = db.query(Attendance).all()
    return {"success": True, "data": records}