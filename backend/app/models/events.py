from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean, BigInteger
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone
from app.database import Base

# event table
class Event(Base):
    __tablename__ = 'events'
    event_id = Column(BigInteger, primary_key=True)
    event_name = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=False)
    archived = Column(Boolean, default=False, nullable=False)
    img_url = Column(String, nullable=True)
    
    booking = relationship("Booking", uselist=False, back_populates="event")