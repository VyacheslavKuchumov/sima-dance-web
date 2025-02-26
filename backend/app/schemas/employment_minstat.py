from pydantic import BaseModel, ConfigDict
from app.schemas.okved_section import OkvedSectionOut


class EmploymentMinstatCreate(BaseModel):
    year: int
    number_of_employees: float
    okved_section_id: int
    salary: float

class EmploymentMinstatUpdate(BaseModel):
    year: int
    number_of_employees: float
    okved_section_id: int
    salary: float
        
class EmploymentMinstatOut(BaseModel):
    id: int
    year: int
    number_of_employees: float
    salary: float
    okved_section: OkvedSectionOut


    
    

    model_config = ConfigDict(from_attributes=True)
