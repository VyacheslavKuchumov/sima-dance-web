from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.events import EventCreate, EventUpdate, EventOut
from app.controllers.events import create_event, get_events, update_event, delete_event, get_archived_events

from app.database import get_db

router = APIRouter()


# get unarchived events
@router.get("/", response_model=list[EventOut])
def get_all_events(db: Session = Depends(get_db)):
    return get_events(db)

# get archived events
@router.get("/archived", response_model=list[EventOut])
def get_archived_events_route(db: Session = Depends(get_db)):
    return get_archived_events(db)


# create a new event
@router.post("/", response_model=EventOut)
def create_event_route(event: EventCreate, db: Session = Depends(get_db)):
    return create_event(db, event)


# update an existing event by id
@router.put("/{event_id}", response_model=EventOut)
def update_event_route(event_id: int, event: EventUpdate, db: Session = Depends(get_db)):
    return update_event(db, event_id, event)


# delete an existing event by id
@router.delete("/{event_id}", response_model=EventOut)
def delete_event_route(event_id: int, db: Session = Depends(get_db)):
    return delete_event(db, event_id)

