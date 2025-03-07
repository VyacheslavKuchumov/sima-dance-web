from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserOut
from app.schemas.seats import SeatOut
from app.schemas.events import EventOut

# schema for bookings
# booking table
# class Booking(Base):
#     __tablename__ = 'bookings'
#     booking_id = Column(BigInteger, primary_key=True)
#     user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
#     seat_id = Column(BigInteger, ForeignKey('seats.seat_id'), nullable=False)
#     event_id = Column(BigInteger, ForeignKey('events.event_id'), nullable=False)
#     booking_date = Column(DateTime, default=datetime.now(timezone.utc))
#     confirmed = Column(Boolean, default=False)
#     paid = Column(Boolean, default=False)
    
#     user = relationship("User", back_populates="booking")
#     seat = relationship("Seat", back_populates="booking")
#     event = relationship("Event", back_populates="booking")
    
# booking create schema
class BookingCreate(BaseModel):
    user_id: int
    seat_id: int
    event_id: int

    

# booking update schema
class BookingUpdate(BaseModel):
    user_id: int
    seat_id: int
    event_id: int
    booking_date: str
    confirmed: bool
    paid: bool

# booking out schema
class BookingOut(BaseModel):
    booking_id: int
    user_id: int
    seat_id: int
    event_id: int
    booking_date: str
    confirmed: bool
    paid: bool
    
    user: UserOut
    seat: SeatOut
    event: EventOut


    model_config = ConfigDict(from_attributes=True)

