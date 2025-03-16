from sqlalchemy.orm import Session
from app.models.bookings import Booking
from app.schemas.bookings import BookingCreate, BookingUpdate
from app.models.seats_in_events import SeatInEvent
from uuid import UUID

import app.controllers.sse as sse

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


# # get all bookings
# def get_bookings(db: Session):
#     return db.query(Booking).all()

# get bookings by event_uid (event_uid is in seats_in_events table that relates to bookings table)
def get_bookings_by_event_uid(db: Session, event_uid: UUID):
    # get all seats_in_events by event_uid
    seats_in_events = db.query(SeatInEvent).filter(SeatInEvent.event_uid == event_uid).order_by(SeatInEvent.seat_in_event_id).all()
    # get all bookings by seat_in_event_id
    bookings = db.query(Booking).filter(Booking.seat_in_event_id.in_([seat.seat_in_event_id for seat in seats_in_events])).all()
    return bookings



# create a new booking and set seat_in_event status to held
def create_booking(db: Session, booking: BookingCreate):
    db_booking = Booking(
        user_uid=booking.user_uid,
        seat_in_event_id=booking.seat_in_event_id,
    )
    db.add(db_booking)
    db.query(SeatInEvent).filter(SeatInEvent.seat_in_event_id == db_booking.seat_in_event_id).update({"status": "held"})
    db.commit()
    db.refresh(db_booking)
    # Prepare the SSE message payload
    sse_payload = {
        "event": "booking_created",
        "data": {
            "status": "held",
            "booking_id": db_booking.booking_id,
            "seat_in_event_id": db_booking.seat_in_event_id,
        },
    }
    
    # Push the SSE notification to the queue
    sse.message(sse_payload)
    return db_booking

# confirm a booking and set seat_in_event status to booked
def confirm_booking(db: Session, booking_id: int):
    # Retrieve the booking first
    db_booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()

    if not db_booking:
        raise ValueError("Booking not found")

    # Update booking confirmation
    db_booking.confirmed = True

    # Update seat status
    db.query(SeatInEvent).filter(SeatInEvent.seat_in_event_id == db_booking.seat_in_event_id).update({"status": "booked"})
    # Prepare the SSE message payload
    

    db.commit()
    sse_payload = {
        "event": "booking_confirmed",
        "data": {
            "status": "booked",
            "booking_id": db_booking.booking_id,
            "seat_in_event_id": db_booking.seat_in_event_id,
        },
    }
    
    # Push the SSE notification to the queue
    sse.message(sse_payload)
    
    db.refresh(db_booking)
    return db_booking


# delete an existing booking by id and set seat_in_event status to available
def delete_booking(db: Session, booking_id: int):
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    db.query(SeatInEvent).filter(SeatInEvent.seat_in_event_id == booking.seat_in_event_id).update({"status": "available"})
    db.delete(booking)
    db.commit()
    # Prepare the SSE message payload
    sse_payload = {
        "event": "booking_deleted",
        "data": {
            "status": "available",
            "booking_id": booking.booking_id,
            "seat_in_event_id": booking.seat_in_event_id,
        },
    }
    
    # Push the SSE notification to the queue
    sse.message(sse_payload)
    return booking

# toggle paid status
def toggle_paid_status(db: Session, booking_id: int):
    db_booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    db_booking.paid = not db_booking.paid
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

