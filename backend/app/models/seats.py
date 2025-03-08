from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean, BigInteger
from sqlalchemy.orm import relationship

from app.database import Base



# Seats table
class Seat(Base):
    __tablename__ = 'seats'
    seat_id = Column(BigInteger, primary_key=True)
    section = Column(String, nullable=False)
    row = Column(String, nullable=False)
    number = Column(String, nullable=False)
    venue_id = Column(BigInteger, ForeignKey('venues.venue_id'), nullable=False)

    venue = relationship("Venue", back_populates="seat")
    seat_in_event = relationship("SeatInEvent", back_populates="seat")
