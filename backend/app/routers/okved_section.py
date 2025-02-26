from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.okved_section import OkvedSectionCreate, OkvedSectionOut
from app.controllers.okved_section import create_okved_section, get_okved_sections, update_okved_section, delete_okved_section
from app.database import get_db

router = APIRouter()


# get all okved sections
@router.get("/", response_model=list[OkvedSectionOut])
def get_all_okved_sections(db: Session = Depends(get_db)):
    return get_okved_sections(db)


# create a new okved section
@router.post("/", response_model=OkvedSectionOut)
def create_okved_section_route(okved_section: OkvedSectionCreate, db: Session = Depends(get_db)):
    return create_okved_section(db, okved_section)


# update an existing okved section by id
@router.put("/{okved_section_id}", response_model=OkvedSectionOut)
def update_okved_section_route(okved_section_id: int, okved_section: OkvedSectionCreate, db: Session = Depends(get_db)):
    return update_okved_section(db, okved_section_id, okved_section)


# delete an existing okved section by id
@router.delete("/{okved_section_id}", response_model=OkvedSectionOut)
def delete_okved_section_route(okved_section_id: int, db: Session = Depends(get_db)):
    return delete_okved_section(db, okved_section_id)
