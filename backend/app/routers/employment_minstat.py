from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.employment_minstat import EmploymentMinstatCreate, EmploymentMinstatUpdate, EmploymentMinstatOut
from app.controllers.employment_minstat import create_employment_minstat, get_employment_minstat, update_employment_minstat, delete_employment_minstat
from app.database import get_db

router = APIRouter()


# get all employment minstat records
@router.get("/", response_model=list[EmploymentMinstatOut])
def get_all_employment_minstat(db: Session = Depends(get_db)):
    return get_employment_minstat(db)


# create a new employment minstat record
@router.post("/", response_model=EmploymentMinstatOut)
def create_employment_minstat_route(employment_minstat: EmploymentMinstatCreate, db: Session = Depends(get_db)):
    return create_employment_minstat(db, employment_minstat)


# update an existing employment minstat record by id
@router.put("/{employment_minstat_id}", response_model=EmploymentMinstatOut)
def update_employment_minstat_route(employment_minstat_id: int, employment_minstat: EmploymentMinstatUpdate, db: Session = Depends(get_db)):
    return update_employment_minstat(db, employment_minstat_id, employment_minstat)


# delete an existing employment minstat record by id
@router.delete("/{employment_minstat_id}", response_model=EmploymentMinstatOut)
def delete_employment_minstat_route(employment_minstat_id: int, db: Session = Depends(get_db)):
    return delete_employment_minstat(db, employment_minstat_id)
