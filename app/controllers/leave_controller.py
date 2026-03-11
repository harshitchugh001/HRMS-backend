from sqlalchemy.orm import Session
from app.models.leave_model import Leave, LeaveStatus
from app.schemas.leave_schema import LeaveCreate, LeaveApproval
from app.models.user_model import User
from fastapi import HTTPException
from datetime import date, datetime


def apply_leave(user_id: int, data: LeaveCreate, db: Session):
    """Employee applies for leave"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate days requested
    start = datetime.strptime(str(data.start_date), "%Y-%m-%d").date()
    end = datetime.strptime(str(data.end_date), "%Y-%m-%d").date()
    
    if start > end:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    days = (end - start).days + 1
    
    leave_record = Leave(
        user_id=user_id,
        leave_type=data.leave_type,
        start_date=start,
        end_date=end,
        reason=data.reason,
        status=LeaveStatus.pending,
        days_requested=days
    )
    
    db.add(leave_record)
    db.commit()
    db.refresh(leave_record)
    
    return {
        "success": True,
        "message": "Leave request submitted",
        "data": {
            "id": leave_record.id,
            "leave_type": leave_record.leave_type,
            "start_date": str(leave_record.start_date),
            "end_date": str(leave_record.end_date),
            "days_requested": leave_record.days_requested,
            "status": leave_record.status
        }
    }


def get_my_leaves(user_id: int, db: Session):
    """Get all leave requests of current user"""
    leaves = db.query(Leave).filter(Leave.user_id == user_id).all()
    
    result = []
    for leave in leaves:
        approver_name = None
        if leave.approved_by:
            approver = db.query(User).filter(User.id == leave.approved_by).first()
            approver_name = approver.full_name if approver else None
        
        result.append({
            "id": leave.id,
            "leave_type": leave.leave_type,
            "start_date": str(leave.start_date),
            "end_date": str(leave.end_date),
            "reason": leave.reason,
            "status": leave.status,
            "days_requested": leave.days_requested,
            "approved_by": approver_name,
            "approval_date": str(leave.approval_date) if leave.approval_date else None
        })
    
    return {"success": True, "data": result}


def get_pending_leaves(db: Session):
    """Get all pending leave requests for HR to approve"""
    leaves = db.query(Leave).filter(Leave.status == LeaveStatus.pending).all()
    
    result = []
    for leave in leaves:
        user = db.query(User).filter(User.id == leave.user_id).first()
        result.append({
            "id": leave.id,
            "user_id": leave.user_id,
            "employee_id": user.employee_id if user else None,
            "employee_name": user.full_name if user else None,
            "department": user.department if user else None,
            "leave_type": leave.leave_type,
            "start_date": str(leave.start_date),
            "end_date": str(leave.end_date),
            "reason": leave.reason,
            "days_requested": leave.days_requested,
            "status": leave.status
        })
    
    return {"success": True, "data": result}


def approve_reject_leave(leave_id: int, data: LeaveApproval, approver_id: int, db: Session):
    """HR Manager approves or rejects a leave request"""
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    if leave.status != LeaveStatus.pending:
        raise HTTPException(status_code=400, detail="Leave already " + leave.status)
    
    if data.status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Status must be 'approved' or 'rejected'")
    
    leave.status = LeaveStatus(data.status)
    leave.approved_by = approver_id
    leave.approval_date = date.today()
    
    db.commit()
    db.refresh(leave)
    
    user = db.query(User).filter(User.id == leave.user_id).first()
    
    return {
        "success": True,
        "message": f"Leave {data.status}",
        "data": {
            "id": leave.id,
            "employee_name": user.full_name if user else None,
            "leave_type": leave.leave_type,
            "status": leave.status,
            "approval_date": str(leave.approval_date)
        }
    }


def get_all_leaves(db: Session):
    """Get all leaves"""
    leaves = db.query(Leave).all()
    
    result = []
    for leave in leaves:
        user = db.query(User).filter(User.id == leave.user_id).first()
        result.append({
            "id": leave.id,
            "employee_id": user.employee_id if user else None,
            "employee_name": user.full_name if user else None,
            "leave_type": leave.leave_type,
            "start_date": str(leave.start_date),
            "end_date": str(leave.end_date),
            "days_requested": leave.days_requested,
            "status": leave.status
        })
    
    return {"success": True, "data": result}
