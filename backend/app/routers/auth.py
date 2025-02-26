from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.controllers import auth as auth_controller
from app.schemas.auth import AuthSignup, AuthSignin, AuthTokens, AuthChangeResponse
from app.database import get_db

router = APIRouter()

@router.post("/signup", response_model=dict)
def signup(auth_data: AuthSignup, db: Session = Depends(get_db)):
    return auth_controller.signup(auth_data, db)

@router.post("/signin", response_model=AuthTokens)
def signin(auth_data: AuthSignin, db: Session = Depends(get_db)):
    return auth_controller.signin(auth_data, db)

@router.post("/changeAccess", response_model=AuthChangeResponse)
def change_access(x_refresh_token: str = Header(...), db: Session = Depends(get_db)):
    return auth_controller.change_access(x_refresh_token, db)
