from fastapi import HTTPException, Header
import jwt
from app.config import settings

def verify_token(x_access_token: str = Header(...)) -> str:
    try:
        payload = jwt.decode(x_access_token, settings.SECRET, algorithms=["HS256"])
        uid = payload.get("uid")
        if uid is None:
            raise HTTPException(status_code=403, detail="Unauthorized")
        return uid
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Unauthorized")
