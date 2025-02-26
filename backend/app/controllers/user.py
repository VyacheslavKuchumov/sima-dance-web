from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserOut

def get_all_users(db: Session):
    users = db.query(User).all()
    if not users:
        raise HTTPException(status_code=404, detail="Users not found")
    return users

def get_user_by_uid(uid: str, db: Session) -> UserOut:
    user = db.query(User).filter(User.user_uid == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_user_by_name(name: str, db: Session) -> UserOut:
    user = db.query(User).filter(User.name == name).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


