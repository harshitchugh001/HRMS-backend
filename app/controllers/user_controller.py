from sqlalchemy.orm import Session
from app.models.user_model import User
from app.schemas.user_schema import UserCreate
from fastapi import HTTPException
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(data: UserCreate, db: Session):
    existing_email = db.query(User).filter(User.email == data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_emp_id = db.query(User).filter(User.employee_id == data.employee_id).first()
    if existing_emp_id:
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    hashed_password = pwd_context.hash(data.password)

    user = User(
        employee_id=data.employee_id,
        full_name=data.full_name,
        email=data.email,
        department=data.department,
        password=hashed_password,
        role_id=data.role_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"success": True, "message": "User created", "data": {"id": user.id, "employee_id": user.employee_id, "email": user.email, "full_name": user.full_name, "department": user.department}}

def get_all_users(db: Session):
    users = db.query(User).all()
    return {"success": True, "data": [{"id": u.id, "employee_id": u.employee_id, "full_name": u.full_name, "email": u.email, "department": u.department, "role_id": u.role_id} for u in users]}

def get_user_by_id(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "data": {"id": user.id, "employee_id": user.employee_id, "full_name": user.full_name, "email": user.email, "department": user.department, "role_id": user.role_id}}

def delete_user(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"success": True, "message": "User deleted"}