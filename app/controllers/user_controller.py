from sqlalchemy.orm import Session
from app.models.user_model import User
from app.schemas.user_schema import UserCreate
from fastapi import HTTPException
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(data: UserCreate, db: Session):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(data.password)

    user = User(
        full_name=data.full_name,
        email=data.email,
        password=hashed_password,
        role_id=data.role_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"success": True, "message": "User created", "data": {"id": user.id, "email": user.email}}

def get_all_users(db: Session):
    users = db.query(User).all()
    return {"success": True, "data": users}

def get_user_by_id(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "data": user}

def delete_user(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"success": True, "message": "User deleted"}