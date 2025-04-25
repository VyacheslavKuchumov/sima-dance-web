from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.bookings import BookingCreate, BookingUpdate, BookingOut
from app.controllers.bookings import create_booking, update_booking, delete_booking, confirm_booking, get_bookings_by_event_uid, toggle_paid_status, toggle_ticket_status
from uuid import UUID

from app.database import get_db

router = APIRouter()


# # get all bookings
# @router.get("/", response_model=list[BookingOut])
# def get_all_bookings(db: Session = Depends(get_db)):
#     return get_bookings(db)

# get bookings by event_uid
@router.get("/event/{event_uid}", response_model=list[BookingOut])
def get_bookings_by_event_uid_route(event_uid: UUID, db: Session = Depends(get_db)):
    return get_bookings_by_event_uid(db, event_uid)



# toggle paid status
@router.put("/payment/{booking_id}", response_model=BookingOut)
def toggle_paid_status_route(booking_id: int, db: Session = Depends(get_db)):
    return toggle_paid_status(db, booking_id)

# create a new booking
@router.post("/", response_model=BookingOut)
async def create_booking_route(booking: BookingCreate, db: Session = Depends(get_db)):
    return await create_booking(db, booking)

# confirm booking
@router.put("/confirm/{booking_id}/{user_uid}", response_model=BookingOut)
async def confirm_booking_route(booking_id: int, user_uid: UUID, db: Session = Depends(get_db)):
    return await confirm_booking(db, booking_id, user_uid)

# toggle ticket confirmed status
@router.put("/ticket/{booking_id}", response_model=BookingOut)
def toggle_ticket_status_route(booking_id: int, db: Session = Depends(get_db)):
    return toggle_ticket_status(db, booking_id)


# delete an existing booking by id
@router.delete("/{booking_id}/{user_uid}", response_model=BookingOut)
async def delete_booking_route(booking_id: int, user_uid: UUID, db: Session = Depends(get_db)):
    return await delete_booking(db, booking_id, user_uid)


# update an existing booking by id
@router.put("/{booking_id}", response_model=BookingOut)
def update_booking_route(booking_id: int, booking: BookingUpdate, db: Session = Depends(get_db)):
    return update_booking(db, booking_id, booking)