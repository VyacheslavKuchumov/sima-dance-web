from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate
from uuid import UUID

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

# edit user's name and child_name by uid
def update_user(user_uid: UUID, user: UserUpdate, db: Session) -> UserOut:
    db_user = db.query(User).filter(User.user_uid == user_uid).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.name = user.name
    db_user.child_name = user.child_name
    db_user.group_name = user.group_name
    db.commit()
    db.refresh(db_user)
    
    return db_user

