from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.attendance_schema import AttendanceCreate
from app.controllers import attendance_controller
from app.dependencies.auth_dependency import get_current_user
from app.models.user_model import User
from sqlalchemy import Integer


router = APIRouter(prefix="/attendance", tags=["Attendance"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.get("/weekly")
def get_weekly_attendance(
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    return attendance_controller.get_weekly_attendance(db)


@router.post("/")
def mark_attendance(
    data:         AttendanceCreate,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    return attendance_controller.mark_attendance(data, db)


@router.get("/")
def get_all_attendance(
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    return attendance_controller.get_all_attendance(db)


@router.get("/{user_id}")
def get_user_attendance(
    user_id:      int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    return attendance_controller.get_attendance_by_user(user_id, db)