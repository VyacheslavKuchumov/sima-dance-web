from sqlalchemy.orm import Session
from app.models.seats import Seat
from app.schemas.seats import SeatCreate, SeatUpdate




# function for getting all seats
def get_seats(db: Session):
    return db.query(Seat).order_by(Seat.seat_id).all()


# function for creating a new seat
def create_seat(db: Session, seat: SeatCreate):
    db_seat = Seat(
        section=seat.section,
        row=seat.row,
        number=seat.number,
        venue_id=seat.venue_id
    )
    db.add(db_seat)
    db.commit()
    db.refresh(db_seat)
    return db_seat


# function for updating an existing seat by id
def update_seat(db: Session, seat_id: int, seat: SeatUpdate):
    db_seat = db.query(Seat).filter(Seat.seat_id == seat_id).first()
    db_seat.section = seat.section
    db_seat.row = seat.row
    db_seat.number = seat.number
    db_seat.venue_id = seat.venue_id
    db.commit()
    db.refresh(db_seat)
    return db_seat


# function for deleting an existing seat by id
def delete_seat(db: Session, seat_id: int):
    seat = db.query(Seat).filter(Seat.seat_id == seat_id).first()
    db.delete(seat)
    db.commit()
    return seat

