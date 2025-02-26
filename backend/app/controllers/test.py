from sqlalchemy.orm import Session
from app.models.test import Test
from app.schemas.test import TestCreate


def create_test(db: Session, test: TestCreate):
    db_test = Test(
        name=test.name,
        description=test.description
    )
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test


def get_test(db: Session, test_id: int):
    return db.query(Test).filter(Test.id == test_id).first()


def get_tests(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Test).offset(skip).limit(limit).all()
