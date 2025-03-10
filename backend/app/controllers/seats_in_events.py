from sqlalchemy.orm import Session
from app.models.seats_in_events import SeatInEvent
from app.models.seats import Seat
from app.schemas.seats_in_events import SeatInEventCreate, SeatInEventUpdate
from uuid import UUID


# from enum import Enum
# from pydantic import BaseModel, Field, ConfigDict
# from app.schemas.seats import SeatOut
# from app.schemas.events import EventOut
# from uuid import UUID


# # Define an Enum for the seat status.
# class SeatStatus(str, Enum):
#     available = "available"
#     held = "held"
#     booked = "booked"
#     unavailable = "unavailable"

# # Schema for creating a seat in an event.
# class SeatInEventCreate(BaseModel):
#     seat_id: int
#     event_uid: UUID
#     status: SeatStatus = SeatStatus.available  # Default is 'available'
#     price: int

# # Schema for updating a seat in an event.
# class SeatInEventUpdate(BaseModel):
#     seat_id: int
#     event_uid: UUID
#     status: SeatStatus
#     price: int

# # Schema for outputting a seat in an event.
# class SeatInEventOut(BaseModel):
#     seat_in_event_id: int
#     seat_id: int
#     event_uid: UUID
#     status: SeatStatus
#     price: int
#     seat: SeatOut
#     event: EventOut

#     model_config = ConfigDict(from_attributes=True)

# initialize seats in event by venue_id and event_uid
def initialize_seats_in_event(db: Session, venue_id: int, event_uid: UUID):
    # get all seats in venue
    seats = db.query(Seat).filter(Seat.venue_id == venue_id).all()
    # create seats in event for each seat
    for seat in seats:
        create_seat_in_event(db, SeatInEventCreate(seat_id=seat.seat_id, event_uid=event_uid, status="available", price=500))
    return get_seats_in_event(db, event_uid)

def get_seats_in_event(db: Session, event_uid: UUID):
    return db.query(SeatInEvent).filter(SeatInEvent.event_uid == event_uid).order_by(SeatInEvent.seat_in_event_id).all()

# function for creating a new seat in an event
def create_seat_in_event(db: Session, seat_in_event: SeatInEventCreate):
    db_seat_in_event = SeatInEvent(
        seat_id=seat_in_event.seat_id,
        event_uid=seat_in_event.event_uid,
        status=seat_in_event.status,
        price=seat_in_event.price,
    )
    db.add(db_seat_in_event)
    db.commit()
    db.refresh(db_seat_in_event)
    return db_seat_in_event

# function for updating an existing seat in an event by id
def update_seat_in_event(db: Session, seat_in_event_id: int, seat_in_event: SeatInEventUpdate):
    db_seat_in_event = db.query(SeatInEvent).filter(SeatInEvent.seat_in_event_id == seat_in_event_id).first()
    db_seat_in_event.seat_id = seat_in_event.seat_id
    db_seat_in_event.event_uid = seat_in_event.event_uid
    db_seat_in_event.status = seat_in_event.status
    db_seat_in_event.price = seat_in_event.price
    db.commit()
    db.refresh(db_seat_in_event)
    return db_seat_in_event

# function for deleting an existing seat in an event by id
def delete_seat_in_event(db: Session, seat_in_event_id: int):
    seat_in_event = db.query(SeatInEvent).filter(SeatInEvent.seat_in_event_id == seat_in_event_id).first()
    db.delete(seat_in_event)
    db.commit()
    return seat_in_event
