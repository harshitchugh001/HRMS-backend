from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.role_model import Role
from app.models.user_model import User
from passlib.context import CryptContext

router = APIRouter(prefix="/setup", tags=["Setup"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/seed")
def seed_data(db: Session = Depends(get_db)):

    
    roles = ["admin", "employee", "manager"]
    for role_name in roles:
        existing = db.query(Role).filter(Role.name == role_name).first()
        if not existing:
            db.add(Role(name=role_name))
    db.commit()

    
    admin_role = db.query(Role).filter(Role.name == "admin").first()

    
    existing_user = db.query(User).filter(User.email == "admin@gmail.com").first()
    if existing_user:
        return {"success": False, "message": "Admin user already exists"}

    admin_user = User(
        employee_id="ADMIN001",
        full_name="Admin",
        email="admin@gmail.com",
        department="Administration",
        password=pwd_context.hash("Admin@123"[:72]),
        role_id=admin_role.id
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    return {
        "success": True,
        "message": "Roles aur Admin user successfully create ho gaye",
        "data": {
            "email": "admin@gmail.com",
            "password": "Admin@123",
            "role": "admin"
        }
    }