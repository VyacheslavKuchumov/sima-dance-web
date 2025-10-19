from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.controllers import user as user_controller
from app.schemas.user import UserSignup, UserSignin, UserTokensOut, UserChangeAccessResponse
from app.database import get_db

router = APIRouter()

@router.post("/signup", response_model=dict)
def signup(auth_data: UserSignup, db: Session = Depends(get_db)):
    return user_controller.signup(auth_data, db)

@router.post("/signin", response_model=UserTokensOut)
def signin(auth_data: UserSignin, db: Session = Depends(get_db)):
    return user_controller.signin(auth_data, db)

@router.post("/changeAccess", response_model=UserChangeAccessResponse)
def change_access(x_refresh_token: str = Header(...), db: Session = Depends(get_db)):
    return user_controller.change_access(x_refresh_token, db)
