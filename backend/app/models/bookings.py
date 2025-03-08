from sqlalchemy import Column, BigInteger, ForeignKey, DateTime, Boolean, UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Booking(Base):
    __tablename__ = 'bookings'
    
    booking_id = Column(BigInteger, primary_key=True)
    user_uid = Column(UUID, ForeignKey('users.user_uid'), nullable=False)
    seat_in_event_id = Column(BigInteger, ForeignKey('seats_in_events.seat_in_event_id'), nullable=False)
    booking_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    confirmed = Column(Boolean, default=False)
    paid = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="booking")
    # The relationship now uses 'booking' as the back_populates name,
    # which should match the attribute name in SeatInEvent.
    seat_in_event = relationship("SeatInEvent", back_populates="booking")
