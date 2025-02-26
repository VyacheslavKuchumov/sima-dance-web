import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.auth import Auth
from app.models.user import User
from app.schemas.auth import AuthSignup, AuthSignin, AuthTokens, AuthChangeResponse
from app.utils import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token

# Define token lifetimes in seconds
ACCESS_LIFETIME = 15 * 60       # 15 minutes
REFRESH_LIFETIME = 60 * 60 * 24 * 60  # 60 days

def signup(auth_data: AuthSignup, db: Session):
    # Check for duplicate email
    existing_auth = db.query(Auth).filter(Auth.email == auth_data.email.lower()).first()
    if existing_auth:
        raise HTTPException(status_code=405, detail="Email is already in use!")
    
    # Create auth record
    new_auth = Auth(
        email=auth_data.email.lower(),
        password=get_password_hash(auth_data.password),
        auth_uid=uuid.uuid4()
    )
    db.add(new_auth)
    db.commit()
    db.refresh(new_auth)
    
    # Create user record
    new_user = User(
        user_uid=new_auth.auth_uid,
        name=auth_data.name,
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "registered", "uid": str(new_user.user_uid)}

def signin(auth_data: AuthSignin, db: Session) -> AuthTokens:
    auth_record = db.query(Auth).filter(Auth.email == auth_data.email.lower()).first()
    if not auth_record:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(auth_data.password, auth_record.password):
        raise HTTPException(status_code=414, detail="Pass is not valid")
    
    # Create tokens
    access_token = create_access_token({"uid": str(auth_record.auth_uid)}, ACCESS_LIFETIME)
    refresh_token = create_refresh_token({"uid": str(auth_record.auth_uid)}, REFRESH_LIFETIME)
    
    # Update record with tokens
    auth_record.AccessToken = access_token
    auth_record.RefreshToken = refresh_token
    db.commit()
    
    return AuthTokens(auth_uid=auth_record.auth_uid, accessToken=access_token, refreshToken=refresh_token)

def change_access(refresh_token: str, db: Session) -> AuthChangeResponse:
    try:
        payload = decode_token(refresh_token)
    except Exception as e:
        raise HTTPException(status_code=403, detail="Unauthorized")
    uid = payload.get("uid")
    if not uid:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    auth_record = db.query(Auth).filter(Auth.auth_uid == uid).first()
    if not auth_record:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_access = create_access_token({"uid": str(auth_record.auth_uid)}, ACCESS_LIFETIME)
    new_refresh = create_refresh_token({"uid": str(auth_record.auth_uid)}, REFRESH_LIFETIME)
    
    auth_record.AccessToken = new_access
    auth_record.RefreshToken = new_refresh
    db.commit()
    
    return AuthChangeResponse(auth_uid=auth_record.auth_uid, accessToken=new_access, refreshToken=new_refresh)
