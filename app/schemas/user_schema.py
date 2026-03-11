from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    department: str
    password: str
    role_id: int

class UserResponse(BaseModel):
    id: int
    employee_id: str
    full_name: str
    email: str
    department: str
    role_id: int

    class Config:
        from_attributes = True
