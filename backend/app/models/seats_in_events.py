from sqlalchemy import Column, BigInteger, ForeignKey, Integer, Enum, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

# Define enum for seat status
class SeatStatus(enum.Enum):
    available = "available"
    held = "held"
    booked = "booked"
    unavailable = "unavailable"

class SeatInEvent(Base):
    __tablename__ = 'seats_in_events'
    
    seat_in_event_id = Column(BigInteger, primary_key=True)
    seat_id = Column(BigInteger, ForeignKey('seats.seat_id'), nullable=False)
    event_uid = Column(UUID, ForeignKey('events.event_uid'), nullable=False)
    status = Column(Enum(SeatStatus), default=SeatStatus.available, nullable=False)
    price = Column(Integer, nullable=True)
    
    seat = relationship("Seat", uselist=False, back_populates="seat_in_event")
    event = relationship("Event", back_populates="seat_in_event")
    # Updated back_populates to match the attribute in Booking
    booking = relationship("Booking", uselist=False, back_populates="seat_in_event")
