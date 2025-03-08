from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.seats_in_events import SeatInEventCreate, SeatInEventUpdate, SeatInEventOut
from app.controllers.seats_in_events import create_seat_in_event, get_seats_in_events, update_seat_in_event, delete_seat_in_event

from app.database import get_db

router = APIRouter()


# get all seats in events
@router.get("/", response_model=list[SeatInEventOut])
def get_all_seats_in_events(db: Session = Depends(get_db)):
    return get_seats_in_events(db)

# create a new seat in an event
@router.post("/", response_model=SeatInEventOut)
def create_seat_in_event_route(seat_in_event: SeatInEventCreate, db: Session = Depends(get_db)):
    return create_seat_in_event(db, seat_in_event)

# update an existing seat in an event by id
@router.put("/{seat_in_event_id}", response_model=SeatInEventOut)
def update_seat_in_event_route(seat_in_event_id: int, seat_in_event: SeatInEventUpdate, db: Session = Depends(get_db)):
    return update_seat_in_event(db, seat_in_event_id, seat_in_event)

# delete an existing seat in an event by id
@router.delete("/{seat_in_event_id}", response_model=SeatInEventOut)
def delete_seat_in_event_route(seat_in_event_id: int, db: Session = Depends(get_db)):
    return delete_seat_in_event(db, seat_in_event_id)



