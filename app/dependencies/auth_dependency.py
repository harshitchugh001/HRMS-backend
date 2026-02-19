from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user_model import User
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role_id: int = payload.get("role")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token is invalid pls login again")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token not verify pls login again")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# ─── Role Guards ──────────────────────────────────────────────────────────────
def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="only admin can access")
    return current_user

def require_manager(current_user: User = Depends(get_current_user)):
    if current_user.role_id not in [1, 3]:  # Admin ya HR Manager
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user