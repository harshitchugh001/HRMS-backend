from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role_id: int

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role_id: int

    class Config:
        from_attributes = True
