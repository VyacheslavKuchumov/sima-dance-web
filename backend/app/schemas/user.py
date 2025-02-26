from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional

class UserOut(BaseModel):
    id: int
    user_uid: UUID
    name: str
    role: str
    

    model_config = ConfigDict(from_attributes=True)

class UserUpdateLikes(BaseModel):
    likes: int
