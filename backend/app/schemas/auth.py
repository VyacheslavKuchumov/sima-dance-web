from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID

class AuthSignup(BaseModel):
    email: EmailStr
    password: str
    name: str

class AuthSignin(BaseModel):
    email: EmailStr
    password: str

class AuthTokens(BaseModel):
    auth_uid: UUID
    accessToken: str
    refreshToken: str

    model_config = ConfigDict(from_attributes=True)

class AuthChangeResponse(BaseModel):
    auth_uid: UUID
    accessToken: str
    refreshToken: str

    model_config = ConfigDict(from_attributes=True)
