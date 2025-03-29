from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.seats_in_events import SeatInEventCreate, SeatInEventUpdate, SeatInEventOut
from app.controllers.seats_in_events import create_seat_in_event, get_seats_in_event, update_seat_in_event, delete_seat_in_event, initialize_seats_in_event
from uuid import UUID
import pickle

from app.database import get_db
from app.redis_client import get_redis_client

router = APIRouter()
redis_client = get_redis_client()

# initialize seats in event by venue_id and event_uid
@router.post("/initialize/{venue_id}/{event_uid}", response_model=list[SeatInEventOut])
def initialize_seats_in_event_route(venue_id: int, event_uid: UUID, db: Session = Depends(get_db)):
    return initialize_seats_in_event(db, venue_id, event_uid)

# get all seats in events
@router.get("/{event_uid}", response_model=list[SeatInEventOut])
def get_seats_in_event_route(event_uid: UUID, db: Session = Depends(get_db)):
    redis_client = get_redis_client()
    seat_ids_key = f"event:{event_uid}:seat_ids"
    
    # Try to retrieve the list of seat IDs
    cached_seat_ids = redis_client.get(seat_ids_key)
    seats_data = []
    if cached_seat_ids:
        seat_ids = pickle.loads(cached_seat_ids)
        seat_keys = [f"event:{event_uid}:seat:{seat_id}" for seat_id in seat_ids]
        cached_seats = redis_client.mget(seat_keys)
        if all(cached_seats):
            seats_data = [pickle.loads(seat) for seat in cached_seats]
            return seats_data

    # Fallback: query the database
    seats = get_seats_in_event(db, event_uid)
    # Convert SQLAlchemy objects to dictionaries using your schema
    seats_data = [SeatInEventOut.from_orm(seat).dict() for seat in seats]
    
    # Cache each seat individually
    seat_ids = []
    pipeline = redis_client.pipeline()
    for seat_dict in seats_data:
        seat_id = seat_dict["seat_in_event_id"]
        seat_ids.append(seat_id)
        key = f"event:{event_uid}:seat:{seat_id}"
        pipeline.setex(key, 300, pickle.dumps(seat_dict))
    pipeline.setex(seat_ids_key, 300, pickle.dumps(seat_ids))
    pipeline.execute()
    
    return seats_data

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



