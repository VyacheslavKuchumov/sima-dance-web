from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.seats import SeatCreate, SeatUpdate, SeatOut
from app.controllers.seats import create_seat, get_seats, update_seat, delete_seat

from app.database import get_db

router = APIRouter()


# get all seats
@router.get("/", response_model=list[SeatOut])
def get_all_seats(db: Session = Depends(get_db)):
    return get_seats(db)


# create a new seat
@router.post("/", response_model=SeatOut)
def create_seat_route(seat: SeatCreate, db: Session = Depends(get_db)):
    return create_seat(db, seat)


# update an existing seat by id
@router.put("/{seat_id}", response_model=SeatOut)
def update_seat_route(seat_id: int, seat: SeatUpdate, db: Session = Depends(get_db)):
    return update_seat(db, seat_id, seat)


# delete an existing seat by id
@router.delete("/{seat_id}", response_model=SeatOut)
def delete_seat_route(seat_id: int, db: Session = Depends(get_db)):
    return delete_seat(db, seat_id)
