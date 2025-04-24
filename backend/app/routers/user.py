from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.controllers import user as user_controller
from app.database import get_db
from app.middlewares.auth import verify_token
from app.schemas.user import UserOut, UserUpdateLikes, UserUpdate
from uuid import UUID

router = APIRouter()

@router.get("/{uid}", response_model=UserOut)
def get_user_by_uid(uid: str, db: Session = Depends(get_db), current_uid: str = Depends(verify_token)):
    # Optionally, enforce that the token owner matches uid.
    return user_controller.get_user_by_uid(uid, db)


# update user 
@router.put("/{user_uid}", response_model=UserOut)
def update_user(user: UserUpdate, user_uid: UUID, db: Session = Depends(get_db)):
    return user_controller.update_user(user_uid, user, db)

# get all users
@router.get("/", response_model=list[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    return user_controller.get_all_users(db)