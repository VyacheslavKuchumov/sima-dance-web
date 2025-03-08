from pydantic import BaseModel, ConfigDict
from app.schemas.venues import VenueOut



# Schema for creating a seat.
class SeatCreate(BaseModel):
    section: str
    row: str
    number: str
    venue_id: int

# Schema for updating a seat.
class SeatUpdate(BaseModel):
    section: str
    row: str
    number: str
    venue_id: int

# Schema for outputting a seat.
class SeatOut(BaseModel):
    seat_id: int
    section: str
    row: str
    number: str
    venue_id: int
    
    venue: VenueOut
    

    model_config = ConfigDict(from_attributes=True)
        