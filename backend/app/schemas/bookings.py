from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserOut
# from app.schemas.seats_in_events import SeatInEventOut
from datetime import datetime

from uuid import UUID


# # booking table
# class Booking(Base):
#     __tablename__ = 'bookings'
#     booking_id = Column(BigInteger, primary_key=True)
#     user_uid = Column(BigInteger, ForeignKey('users.user_uid'), nullable=False)
#     seat_in_event_id = Column(BigInteger, ForeignKey('seats_in_events.seat_in_event_id'), nullable=False)
#     booking_date = Column(DateTime, default=datetime.now(timezone.utc))
#     confirmed = Column(Boolean, default=False)
#     paid = Column(Boolean, default=False)
    
#     user = relationship("User", back_populates="booking")
#     seat_in_event = relationship("SeatInEvent", back_populates="booking")

    
# booking create schema
class BookingCreate(BaseModel):
    user_uid: UUID
    seat_in_event_id: int

# booking_date = Column(DateTime, default=datetime.now(timezone.utc))
# booking update schema
class BookingUpdate(BaseModel):
    user_uid: UUID
    seat_in_event_id: int
    booking_date: datetime
    confirmed: bool
    paid: bool
    
# booking out schema
class BookingOut(BaseModel):
    booking_id: int
    user_uid: UUID
    seat_in_event_id: int
    booking_date: datetime
    confirmed: bool
    paid: bool
    ticket_confirmed: bool
    
    user: UserOut
    # seat_in_event: SeatInEventOut

    model_config = ConfigDict(from_attributes=True)

