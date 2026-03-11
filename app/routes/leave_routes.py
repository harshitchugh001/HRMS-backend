from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.auth_dependency import get_db, get_current_user, require_manager
from app.schemas.leave_schema import LeaveCreate, LeaveApproval
from app.controllers import leave_controller
from app.models.user_model import User

router = APIRouter(prefix="/leaves", tags=["Leaves"])


@router.post("/apply")
def apply_leave(
    data: LeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Employee applies for leave"""
    return leave_controller.apply_leave(current_user.id, data, db)


@router.get("/my-leaves")
def get_my_leaves(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's leave requests"""
    return leave_controller.get_my_leaves(current_user.id, db)


@router.get("/pending")
def get_pending_leaves(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Get all pending leave requests (HR Manager only)"""
    return leave_controller.get_pending_leaves(db)


@router.post("/approve")
def approve_reject_leave(
    data: LeaveApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """HR Manager approves or rejects a leave request"""
    return leave_controller.approve_reject_leave(data.leave_id, data, current_user.id, db)


@router.get("/all")
def get_all_leaves(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Get all leaves"""
    return leave_controller.get_all_leaves(db)
