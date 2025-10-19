from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate, UserSignup, UserSignin, UserTokensOut, UserChangeAccessResponse
from app.utils import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from uuid import UUID


# Define token lifetimes in seconds
ACCESS_LIFETIME = 15 * 60       # 15 minutes
REFRESH_LIFETIME = 60 * 60 * 24 * 60  # 60 days



def signup(user_data: UserSignup, db: Session):
    # Check for duplicate email
    existing_user = db.query(User).filter(User.email == user_data.email.lower()).first()
    if existing_user:
        raise HTTPException(status_code=405, detail="Пользователь с таким email уже существует!")

    # Create user record
    new_user = User(
        email=user_data.email.lower(),
        password=get_password_hash(user_data.password),
        name=user_data.name,
        child_name=user_data.child_name,
        group_name=user_data.group_name,
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Регистрация прошла успешно!", "uid": str(new_user.user_uid)}

def signin(user_data: UserSignin, db: Session) -> UserTokensOut:
    user_record = db.query(User).filter(User.email == user_data.email.lower()).first()
    if not user_record:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if not verify_password(user_data.password, user_record.password):
        raise HTTPException(status_code=414, detail="Пароль невереный")

    # Create tokens
    access_token = create_access_token({"uid": str(user_record.user_uid)}, ACCESS_LIFETIME)
    refresh_token = create_refresh_token({"uid": str(user_record.user_uid)}, REFRESH_LIFETIME)

    # Update record with tokens
    user_record.AccessToken = access_token
    user_record.RefreshToken = refresh_token
    db.commit()

    return UserTokensOut(uid=user_record.user_uid, accessToken=access_token, refreshToken=refresh_token)

def change_access(refresh_token: str, db: Session) -> UserChangeAccessResponse:
    try:
        payload = decode_token(refresh_token)
    except Exception as e:
        raise HTTPException(status_code=403, detail="Unauthorized")
    uid = payload.get("uid")
    if not uid:
        raise HTTPException(status_code=403, detail="Unauthorized")

    user_record = db.query(User).filter(User.user_uid == uid).first()
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")

    new_access = create_access_token({"uid": str(user_record.user_uid)}, ACCESS_LIFETIME)
    new_refresh = create_refresh_token({"uid": str(user_record.user_uid)}, REFRESH_LIFETIME)

    user_record.AccessToken = new_access
    user_record.RefreshToken = new_refresh
    db.commit()

    return UserChangeAccessResponse(uid=user_record.user_uid, accessToken=new_access, refreshToken=new_refresh)

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

