from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean, BigInteger
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone
from app.database import Base

# booking table
class Booking(Base):
    __tablename__ = 'bookings'
    booking_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    seat_id = Column(BigInteger, ForeignKey('seats.seat_id'), nullable=False)
    event_id = Column(BigInteger, ForeignKey('events.event_id'), nullable=False)
    booking_date = Column(DateTime, default=datetime.now(timezone.utc))
    confirmed = Column(Boolean, default=False)
    paid = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="booking")
    seat = relationship("Seat", back_populates="booking")
    event = relationship("Event", back_populates="booking")
    
   