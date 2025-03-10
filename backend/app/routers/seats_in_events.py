from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.seats_in_events import SeatInEventCreate, SeatInEventUpdate, SeatInEventOut
from app.controllers.seats_in_events import create_seat_in_event, get_seats_in_event, update_seat_in_event, delete_seat_in_event, initialize_seats_in_event
from uuid import UUID

from app.database import get_db

router = APIRouter()

# initialize seats in event by venue_id and event_uid
@router.post("/initialize/{venue_id}/{event_uid}", response_model=list[SeatInEventOut])
def initialize_seats_in_event_route(venue_id: int, event_uid: UUID, db: Session = Depends(get_db)):
    return initialize_seats_in_event(db, venue_id, event_uid)

# get all seats in events
@router.get("/{event_uid}", response_model=list[SeatInEventOut])
def get_seats_in_event_route(event_uid: UUID, db: Session = Depends(get_db)):
    return get_seats_in_event(db, event_uid)

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



