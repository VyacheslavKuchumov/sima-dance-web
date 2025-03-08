from sqlalchemy.orm import Session
from app.models.bookings import Booking
from app.schemas.bookings import BookingCreate, BookingUpdate

# # # booking table
# # class Booking(Base):
# #     __tablename__ = 'bookings'
# #     booking_id = Column(BigInteger, primary_key=True)
# #     user_uid = Column(BigInteger, ForeignKey('users.user_uid'), nullable=False)
# #     seat_in_event_id = Column(BigInteger, ForeignKey('seats_in_events.seat_in_event_id'), nullable=False)
# #     booking_date = Column(DateTime, default=datetime.now(timezone.utc))
# #     confirmed = Column(Boolean, default=False)
# #     paid = Column(Boolean, default=False)
    
# #     user = relationship("User", back_populates="booking")
# #     seat_in_event = relationship("SeatInEvent", back_populates="booking")

    
# # booking create schema
# class BookingCreate(BaseModel):
#     user_uid: int
#     seat_in_event_id: int
    
# # booking update schema
# class BookingUpdate(BaseModel):
#     user_uid: int
#     seat_in_event_id: int
#     booking_date: str
#     confirmed: bool
#     paid: bool
    
# # booking out schema
# class BookingOut(BaseModel):
#     booking_id: int
#     user_uid: int
#     seat_in_event_id: int
#     booking_date: str
#     confirmed: bool
#     paid: bool
    
#     user: UserOut
#     seat_in_event: SeatInEventOut

#     model_config = ConfigDict(from_attributes=True)


# get all bookings
def get_bookings(db: Session):
    return db.query(Booking).all()

# create a new booking
def create_booking(db: Session, booking: BookingCreate):
    db_booking = Booking(
        user_uid=booking.user_uid,
        seat_in_event_id=booking.seat_in_event_id,
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

# update an existing booking by id
def update_booking(db: Session, booking_id: int, booking: BookingUpdate):
    db_booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    db_booking.user_uid = booking.user_uid
    db_booking.seat_in_event_id = booking.seat_in_event_id
    db_booking.booking_date = booking.booking_date
    db_booking.confirmed = booking.confirmed
    db_booking.paid = booking.paid
    db.commit()
    db.refresh(db_booking)
    return db_booking

# delete an existing booking by id
def delete_booking(db: Session, booking_id: int):
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    db.delete(booking)
    db.commit()
    return booking