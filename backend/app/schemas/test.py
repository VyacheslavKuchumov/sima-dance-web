from pydantic import BaseModel, ConfigDict

class TestBase(BaseModel):
    pass

class TestCreate(TestBase):
    name: str
    description: str

class TestOut(TestBase):
    id: int
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)
