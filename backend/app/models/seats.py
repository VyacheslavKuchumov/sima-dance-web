from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean, BigInteger
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.database import Base

# Enum for seat status
class SeatStatus(enum.Enum):
    available = "available"
    held = "held"
    booked = "booked"
    unavailable = "unavailable"

# Seats table
class Seat(Base):
    __tablename__ = 'seats'
    seat_id = Column(BigInteger, primary_key=True)
    row = Column(String, nullable=False)
    number = Column(String, nullable=False)
    status = Column(Enum(SeatStatus), default=SeatStatus.available, nullable=False)
    price = Column(Integer, nullable=True)
    
    booking = relationship("Booking", uselist=False, back_populates="seat")


