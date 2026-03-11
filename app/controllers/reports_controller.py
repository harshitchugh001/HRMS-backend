from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user_model import User
from app.models.attendance_model import Attendance
from datetime import date, timedelta


def get_employee_statistics(db: Session):
    """Get overall employee statistics"""
    total_employees = db.query(func.count(User.id)).filter(User.role_id == 2).scalar() or 0
    total_managers = db.query(func.count(User.id)).filter(User.role_id == 3).scalar() or 0
    total_users = total_employees + total_managers
    
    return {
        "success": True,
        "data": {
            "total_employees": total_employees,
            "total_managers": total_managers,
            "total_users": total_users
        }
    }


def get_department_summary(db: Session):
    """Get attendance summary by department"""
    today = date.today()
    month_start = today.replace(day=1)
    
    departments = db.query(User.department).distinct().filter(User.role_id == 2).all()
    
    result = []
    for (dept,) in departments:
        total_emp = db.query(func.count(User.id)).filter(
            User.department == dept,
            User.role_id == 2
        ).scalar() or 0
        
        present_count = db.query(func.count(Attendance.id)).filter(
            Attendance.user_id.in_(
                db.query(User.id).filter(User.department == dept, User.role_id == 2)
            ),
            Attendance.date >= month_start,
            Attendance.date <= today,
            Attendance.status == "present"
        ).scalar() or 0
        
        absent_count = db.query(func.count(Attendance.id)).filter(
            Attendance.user_id.in_(
                db.query(User.id).filter(User.department == dept, User.role_id == 2)
            ),
            Attendance.date >= month_start,
            Attendance.date <= today,
            Attendance.status == "absent"
        ).scalar() or 0
        
        pct = round((present_count / (present_count + absent_count) * 100)) if (present_count + absent_count) > 0 else 0
        
        result.append({
            "department": dept,
            "total_employees": total_emp,
            "present": present_count,
            "absent": absent_count,
            "percentage": pct
        })
    
    return {"success": True, "data": result}


def get_employee_attendance_report(db: Session):
    """Get detailed employee-wise attendance report"""
    today = date.today()
    month_start = today.replace(day=1)
    
    employees = db.query(User).filter(User.role_id == 2).all()
    
    result = []
    for emp in employees:
        present_count = db.query(func.count(Attendance.id)).filter(
            Attendance.user_id == emp.id,
            Attendance.date >= month_start,
            Attendance.date <= today,
            Attendance.status == "present"
        ).scalar() or 0
        
        absent_count = db.query(func.count(Attendance.id)).filter(
            Attendance.user_id == emp.id,
            Attendance.date >= month_start,
            Attendance.date <= today,
            Attendance.status == "absent"
        ).scalar() or 0
        
        total_marked = present_count + absent_count
        pct = round((present_count / total_marked * 100)) if total_marked > 0 else 0
        
        result.append({
            "employee_id": emp.employee_id,
            "full_name": emp.full_name,
            "department": emp.department,
            "email": emp.email,
            "present": present_count,
            "absent": absent_count,
            "percentage": pct
        })
    
    return {"success": True, "data": result}


def get_attendance_trend(db: Session):
    """Get attendance trend for last 30 days"""
    today = date.today()
    thirty_days_ago = today - timedelta(days=29)
    
    records = db.query(
        Attendance.date,
        func.count(Attendance.id).label("total"),
        func.sum(
            func.cast(Attendance.status == "present", func.Integer)
        ).label("present_count")
    ).filter(
        Attendance.date >= thirty_days_ago,
        Attendance.date <= today
    ).group_by(Attendance.date).order_by(Attendance.date).all()
    
    result = []
    for r in records:
        pct = round((r.present_count / r.total * 100)) if r.total > 0 else 0
        result.append({
            "date": str(r.date),
            "total": r.total,
            "present": r.present_count or 0,
            "absent": r.total - (r.present_count or 0),
            "percentage": pct
        })
    
    return {"success": True, "data": result}


def get_today_summary(db: Session):
    """Get today's attendance summary"""
    today = date.today()
    
    total_emp = db.query(func.count(User.id)).filter(User.role_id == 2).scalar() or 0
    present_today = db.query(func.count(Attendance.id)).filter(
        Attendance.date == today,
        Attendance.status == "present"
    ).scalar() or 0
    absent_today = db.query(func.count(Attendance.id)).filter(
        Attendance.date == today,
        Attendance.status == "absent"
    ).scalar() or 0
    not_marked = total_emp - (present_today + absent_today)
    pct = round((present_today / total_emp * 100)) if total_emp > 0 else 0
    
    return {
        "success": True,
        "data": {
            "total_employees": total_emp,
            "present": present_today,
            "absent": absent_today,
            "not_marked": not_marked,
            "percentage": pct
        }
    }
