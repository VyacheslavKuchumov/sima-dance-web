from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID

class UserSignup(BaseModel):
    email: EmailStr
    password: str
    name: str
    child_name: str
    group_name: str

class UserSignin(BaseModel):
    email: EmailStr
    password: str

class UserTokensOut(BaseModel):
    uid: UUID
    accessToken: str
    refreshToken: str

    model_config = ConfigDict(from_attributes=True)

class UserChangeAccessResponse(BaseModel):
    user_uid: UUID
    accessToken: str
    refreshToken: str

    model_config = ConfigDict(from_attributes=True)
class UserUpdate(BaseModel):
    name: str
    child_name: str
    group_name: str

class UserOut(BaseModel):
    id: int
    user_uid: UUID
    name: str
    child_name: str
    group_name: str
    role: str
    

    model_config = ConfigDict(from_attributes=True)



