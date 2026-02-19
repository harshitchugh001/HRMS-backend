from sqlalchemy.orm import Session
from app.models import User
from app.schemas.user_schema import UserCreate
from app.core.security import hash_password
from fastapi import HTTPException

def create_user(data: UserCreate, db: Session):

    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        full_name=data.full_name,
        email=data.email,
        password=hash_password(data.password),
        role_id=data.role_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
