from pydantic import BaseModel
from datetime import date
from typing import Optional

class AttendanceCreate(BaseModel):
    user_id: int
    date: date
    status: str  

class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    date: date
    status: str

    class Config:
        from_attributes = True