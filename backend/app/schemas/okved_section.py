from pydantic import BaseModel, ConfigDict



class OkvedSectionCreate(BaseModel):
    code: str
    name: str

class OkvedSectionUpdate(BaseModel):
    code: str
    name: str
    

class OkvedSectionOut(BaseModel):
    id: int
    code: str
    name: str
    

    model_config = ConfigDict(from_attributes=True)
