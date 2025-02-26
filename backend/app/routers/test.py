from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.test import TestCreate, TestOut
from app.controllers.test import create_test, get_test, get_tests
from app.database import get_db

router = APIRouter()


@router.post("/", response_model=TestOut)
def create_test_endpoint(test: TestCreate, db: Session = Depends(get_db)):
    return create_test(db, test)


@router.get("/{test_id}", response_model=TestOut)
def get_test_endpoint(test_id: int, db: Session = Depends(get_db)):
    test = get_test(db, test_id)
    if test is None:
        raise HTTPException(status_code=404, detail="User not found")
    return test


@router.get("/", response_model=list[TestOut])
def get_tests_endpoint(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_tests(db, skip, limit)

