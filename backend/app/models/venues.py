from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean, BigInteger
from sqlalchemy.orm import relationship

from app.database import Base



# Venues table
class Venue(Base):
    __tablename__ = 'venues'
    venue_id = Column(BigInteger, primary_key=True)
    venue_name = Column(String, nullable=False)
    
    seat = relationship("Seat", back_populates="venue")
    