from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional


class UserUpdateLikes(BaseModel):
    likes: int

class UserUpdate(BaseModel):
    name: str
    child_name: str

class UserOut(BaseModel):
    id: int
    user_uid: UUID
    name: str
    child_name: str
    role: str
    

    model_config = ConfigDict(from_attributes=True)



