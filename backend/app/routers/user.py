from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.controllers import user as user_controller
from app.database import get_db
from app.middlewares.auth import verify_token
from app.schemas.user import UserOut, UserUpdateLikes

router = APIRouter()

@router.get("/{uid}", response_model=UserOut)
def get_user_by_uid(uid: str, db: Session = Depends(get_db), current_uid: str = Depends(verify_token)):
    # Optionally, enforce that the token owner matches uid.
    return user_controller.get_user_by_uid(uid, db)


