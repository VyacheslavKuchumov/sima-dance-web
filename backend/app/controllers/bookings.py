from sqlalchemy.orm import Session
from app.models.bookings import Booking
from app.schemas.bookings import BookingCreate, BookingUpdate


# # booking create schema
# class BookingCreate(BaseModel):
#     user_id: int
#     seat_id: int
#     event_id: int
#     booking_date: str
    

# # booking update schema
# class BookingUpdate(BaseModel):
#     user_id: int
#     seat_id: int
#     event_id: int
#     booking_date: str
#     confirmed: bool
#     paid: bool

# # booking out schema
# class BookingOut(BaseModel):
#     booking_id: int
#     user_id: int
#     seat_id: int
#     event_id: int
#     booking_date: str
#     confirmed: bool
#     paid: bool
    
#     user: UserOut
#     seat: SeatOut
#     event: EventOut


#     model_config = ConfigDict(from_attributes=True)


# function for getting all bookings
def get_bookings(db: Session):
    return db.query(Booking).order_by(Booking.booking_id).all()


# function for creating a new booking
def create_booking(db: Session, booking: BookingCreate):
    db_booking = Booking(
        user_id=booking.user_id,
        seat_id=booking.seat_id,
        event_id=booking.event_id,
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


# function for updating an existing booking by id
def update_booking(db: Session, booking_id: int, booking: BookingUpdate):
    db_booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    db_booking.user_id = booking.user_id
    db_booking.seat_id = booking.seat_id
    db_booking.event_id = booking.event_id
    db_booking.booking_date = booking.booking_date
    db_booking.confirmed = booking.confirmed
    db_booking.paid = booking.paid
    db.commit()
    db.refresh(db_booking)
    return db_booking


# function for deleting an existing booking by id
def delete_booking(db: Session, booking_id: int):
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    db.delete(booking)
    db.commit()
    return booking

