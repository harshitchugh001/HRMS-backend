from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.auth_dependency import get_db, get_current_user, require_admin, require_manager
from app.schemas.user_schema import UserCreate
from app.controllers import user_controller
from app.models.user_model import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/")
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id == 1 and data.role_id != 3:
        raise HTTPException(status_code=403, detail="Admin can create only hr manager")
    if current_user.role_id == 3 and data.role_id != 2:
        raise HTTPException(status_code=403, detail="HR Manager can create only employee")
    if current_user.role_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="employee can't create the users")

    return user_controller.create_user(data, db)

@router.get("/")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)  
):
    return user_controller.get_all_users(db)

@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return user_controller.get_user_by_id(user_id, db)

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  
):
    return user_controller.delete_user(user_id, db)