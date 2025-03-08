from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.venues import VenueCreate, VenueUpdate, VenueOut
from app.controllers.venues import create_venue, get_venues, update_venue, delete_venue

from app.database import get_db

router = APIRouter()


# get all venues
@router.get("/", response_model=list[VenueOut])
def get_all_venues(db: Session = Depends(get_db)):
    return get_venues(db)

# create a new venue
@router.post("/", response_model=VenueOut)
def create_venue_route(venue: VenueCreate, db: Session = Depends(get_db)):
    return create_venue(db, venue)

# update an existing venue by id
@router.put("/{venue_id}", response_model=VenueOut)
def update_venue_route(venue_id: int, venue: VenueUpdate, db: Session = Depends(get_db)):
    return update_venue(db, venue_id, venue)

# delete an existing venue by id
@router.delete("/{venue_id}", response_model=VenueOut)
def delete_venue_route(venue_id: int, db: Session = Depends(get_db)):
    return delete_venue(db, venue_id)
