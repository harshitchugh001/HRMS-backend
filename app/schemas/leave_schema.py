from pydantic import BaseModel
from datetime import date
from typing import Optional

class LeaveCreate(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None

class LeaveResponse(BaseModel):
    id: int
    user_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str]
    status: str
    days_requested: int
    approved_by: Optional[int]
    approval_date: Optional[date]

    class Config:
        from_attributes = True

class LeaveApproval(BaseModel):
    leave_id: int
    status: str  # approved or rejected
