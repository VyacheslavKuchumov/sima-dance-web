from sqlalchemy.orm import Session
from app.models.employment_minstat import EmploymentMinstat
from app.schemas.employment_minstat import EmploymentMinstatCreate, EmploymentMinstatUpdate

# function for getting all employment minstat records
def get_employment_minstat(db: Session):
    return db.query(EmploymentMinstat).order_by(EmploymentMinstat.year).all()


# function for creating a new employment minstat record
def create_employment_minstat(db: Session, employment_minstat: EmploymentMinstatCreate):
    db_employment_minstat = EmploymentMinstat(
        year=employment_minstat.year,
        number_of_employees=employment_minstat.number_of_employees,
        okved_section_id=employment_minstat.okved_section_id,
        salary=employment_minstat.salary
    )
    db.add(db_employment_minstat)
    db.commit()
    db.refresh(db_employment_minstat)
    return db_employment_minstat


# function for updating an existing employment minstat record by id
def update_employment_minstat(db: Session, employment_minstat_id: int, employment_minstat: EmploymentMinstatUpdate):
    db_employment_minstat = db.query(EmploymentMinstat).filter(EmploymentMinstat.id == employment_minstat_id).first()
    db_employment_minstat.year = employment_minstat.year
    db_employment_minstat.number_of_employees = employment_minstat.number_of_employees
    db_employment_minstat.okved_section_id = employment_minstat.okved_section_id
    db_employment_minstat.salary = employment_minstat.salary
    db.commit()
    db.refresh(db_employment_minstat)
    return db_employment_minstat


# function for deleting an existing employment minstat record by id
def delete_employment_minstat(db: Session, employment_minstat_id: int):
    employment_minstat = db.query(EmploymentMinstat).filter(EmploymentMinstat.id == employment_minstat_id).first()
    db.delete(employment_minstat)
    db.commit()
    return employment_minstat