import json
from sqlalchemy.orm import Session
from app.models.bookings import Booking
from app.schemas.bookings import BookingCreate, BookingUpdate
from app.models.seats_in_events import SeatInEvent
from uuid import UUID
from app.websocket.connectionManager import manager  # Import your WebSocket connection manager

from app.controllers.redis import update_seat_cache


# get all bookings
def get_bookings(db: Session):
    return db.query(Booking).all()

# get bookings by event_uid (event_uid is in seats_in_events table that relates to bookings table)
def get_bookings_by_event_uid(db: Session, event_uid: UUID):
    # get all seats_in_events by event_uid
    seats_in_events = (
        db.query(SeatInEvent)
        .filter(SeatInEvent.event_uid == event_uid)
        .order_by(SeatInEvent.seat_in_event_id)
        .all()
    )
    # get all bookings by seat_in_event_id
    bookings = db.query(Booking).filter(
        Booking.seat_in_event_id.in_(
            [seat.seat_in_event_id for seat in seats_in_events]
        )
    ).all()
    return bookings

# create a new booking and set seat_in_event status to held
async def create_booking(db: Session, booking: BookingCreate):
    db_booking = Booking(
        user_uid=booking.user_uid,
        seat_in_event_id=booking.seat_in_event_id,
    )
    db.add(db_booking)
    
    # Retrieve the actual SeatInEvent record using .first()
    db_seat_in_event = db.query(SeatInEvent).filter(
        SeatInEvent.seat_in_event_id == db_booking.seat_in_event_id
    ).first()
    if db_seat_in_event.status != "available":
        raise ValueError("Seat is not available")
    db_seat_in_event.status = "held"
    db.commit()
    
    db.refresh(db_booking)
    
    # Update the cache for this seat
    update_seat_cache(db_seat_in_event)
    
    # Prepare the WebSocket message payload
    payload = {
        "event": "booking_created",
        "data": {
            "status": "held",
            "booking_id": db_booking.booking_id,
            "seat_in_event_id": db_seat_in_event.seat_in_event_id,
        },
    }
    
    
    
    # Broadcast the notification to all connected WebSocket clients
    await manager.broadcast(json.dumps(payload))
    
    return db_booking

# confirm a booking and set seat_in_event status to booked
async def confirm_booking(db: Session, booking_id: int, user_uid: UUID):
    # Retrieve the booking first
    db_booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()

    if not db_booking:
        raise ValueError("Booking not found")
    if db_booking.user_uid != user_uid:
        raise ValueError("User not authorized to confirm this booking")

    # Update booking confirmation
    db_booking.confirmed = True

    # Retrieve the SeatInEvent instance with .first() and update its status
    db_seat_in_event = db.query(SeatInEvent).filter(
        SeatInEvent.seat_in_event_id == db_booking.seat_in_event_id
    ).first()
    if db_seat_in_event.status != "held":
        raise ValueError("Seat is not held")
    db_seat_in_event.status = "booked"

    db.commit()
    db.refresh(db_booking)
    
    # Update the cache for this seat
    update_seat_cache(db_seat_in_event)
    
    payload = {
        "event": "booking_confirmed",
        "data": {
            "status": "booked",
            "booking_id": db_booking.booking_id,
            "seat_in_event_id": db_seat_in_event.seat_in_event_id,
        },
    }
    
    await manager.broadcast(json.dumps(payload))
    
    return db_booking

# delete an existing booking by id and set seat_in_event status to available
async def delete_booking(db: Session, booking_id: int, user_uid: UUID):
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if not booking:
        raise ValueError("Booking not found")
    if booking.user_uid != user_uid:
        raise ValueError("User not authorized to delete this booking")
    seat_in_event = db.query(SeatInEvent).filter(
        SeatInEvent.seat_in_event_id == booking.seat_in_event_id
    ).first()
    seat_in_event.status = "available"
    db.delete(booking)
    db.commit()

    # Update the cache for this seat
    update_seat_cache(seat_in_event)
    
    payload = {
        "event": "booking_deleted",
        "data": {
            "status": "available",
            "seat_in_event_id": seat_in_event.seat_in_event_id,
        },
    }
    
    await manager.broadcast(json.dumps(payload))
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
