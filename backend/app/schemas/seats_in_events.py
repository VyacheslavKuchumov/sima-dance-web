from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.seats import SeatOut
from app.schemas.events import EventOut
from uuid import UUID



# Schema for creating a seat in an event.
class SeatInEventCreate(BaseModel):
    seat_id: int
    event_uid: UUID
    status: str  
    price: int

# Schema for updating a seat in an event.
class SeatInEventUpdate(BaseModel):
    seat_id: int
    event_uid: UUID
    status: str
    price: int

# Schema for outputting a seat in an event.
class SeatInEventOut(BaseModel):
    seat_in_event_id: int
    seat_id: int
    event_uid: UUID
    status: str
    price: int
    seat: SeatOut
    event: EventOut

    model_config = ConfigDict(from_attributes=True)
