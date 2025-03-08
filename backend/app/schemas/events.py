from pydantic import BaseModel, ConfigDict
from datetime import date
from uuid import UUID


# schema for events
# event table
# class Event(Base):
#     __tablename__ = 'events'
#     event_id = Column(BigInteger, primary_key=True)
#     event_name = Column(String, nullable=False)
#     event_date = Column(DateTime, nullable=False)
#     archived = Column(Boolean, default=False)
#     img_url = Column(String, nullable=True)
    
#     booking = relationship("Booking", uselist=False, back_populates="event")

# event create schema
class EventCreate(BaseModel):
    event_name: str
    event_date: date
    img_url: str

# event update schema
class EventUpdate(BaseModel):
    event_name: str
    event_date: date
    img_url: str
    archived: bool

# event out schema
class EventOut(BaseModel):
    event_id: int
    event_uid: UUID
    event_name: str
    event_date: date
    img_url: str
    archived: bool


    model_config = ConfigDict(from_attributes=True)
