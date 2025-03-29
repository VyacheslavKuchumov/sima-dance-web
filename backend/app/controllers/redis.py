import pickle
from app.schemas.seats_in_events import SeatInEventOut
from app.redis_client import get_redis_client

def update_seat_cache(seat):
    """
    Update the Redis cache for a single seat in an event.
    Converts the SQLAlchemy model to a serializable dict using the Pydantic schema.
    """
    redis_client = get_redis_client()
    # Convert the seat to a dict (make sure relationships are eagerly loaded or already serialized)
    seat_data = SeatInEventOut.from_orm(seat).dict()
    cache_key = f"event:{seat.event_uid}:seat:{seat.seat_in_event_id}"
    # Cache for 300 seconds (adjust as needed)
    redis_client.setex(cache_key, 300, pickle.dumps(seat_data))
