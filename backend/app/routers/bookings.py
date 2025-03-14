from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.bookings import BookingCreate, BookingUpdate, BookingOut
from app.controllers.bookings import create_booking, get_bookings, update_booking, delete_booking, confirm_booking

from app.database import get_db

router = APIRouter()


# get all bookings
@router.get("/", response_model=list[BookingOut])
def get_all_bookings(db: Session = Depends(get_db)):
    return get_bookings(db)

# confirm booking
@router.put("/confirm/{booking_id}", response_model=BookingOut)
def confirm_booking_route(booking_id: int, db: Session = Depends(get_db)):
    return confirm_booking(db, booking_id)

# create a new booking
@router.post("/", response_model=BookingOut)
def create_booking_route(booking: BookingCreate, db: Session = Depends(get_db)):
    return create_booking(db, booking)



# update an existing booking by id
@router.put("/{booking_id}", response_model=BookingOut)
def update_booking_route(booking_id: int, booking: BookingUpdate, db: Session = Depends(get_db)):
    return update_booking(db, booking_id, booking)


# delete an existing booking by id
@router.delete("/{booking_id}", response_model=BookingOut)
def delete_booking_route(booking_id: int, db: Session = Depends(get_db)):
    return delete_booking(db, booking_id)
