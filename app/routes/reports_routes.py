from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.auth_dependency import get_db, get_current_user, require_manager
from app.controllers import reports_controller
from app.models.user_model import User

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/statistics")
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Get overall employee statistics"""
    return reports_controller.get_employee_statistics(db)


@router.get("/departments")
def get_department_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Get attendance summary by department"""
    return reports_controller.get_department_summary(db)


@router.get("/employees")
def get_employee_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Get detailed employee-wise attendance report"""
    return reports_controller.get_employee_attendance_report(db)


@router.get("/trend")
def get_attendance_trend(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Get attendance trend for last 30 days"""
    return reports_controller.get_attendance_trend(db)


@router.get("/today")
def get_today_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Get today's attendance summary"""
    return reports_controller.get_today_summary(db)
