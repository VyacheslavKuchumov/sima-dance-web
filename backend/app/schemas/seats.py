from pydantic import BaseModel, ConfigDict

# schema for seats
# Enum for seat status
# class SeatStatus(enum.Enum):
#     available = "available"
#     held = "held"
#     booked = "booked"
#     unavailable = "unavailable"

# Seats table
# class Seat(Base):
#     __tablename__ = 'seats'
#     seat_id = Column(BigInteger, primary_key=True)
#     row = Column(String, nullable=False)
#     number = Column(String, nullable=False)
#     status = Column(Enum(SeatStatus), default=SeatStatus.available, nullable=False)
#     price = Column(Integer, nullable=True)
    
#     booking = relationship("Booking", uselist=False, back_populates="seat")

# seat create schema
class SeatCreate(BaseModel):
    row: str
    number: str
    status: str
    price: int
    
# seat update schema
class SeatUpdate(BaseModel):
    row: str
    number: str
    status: str
    price: int

# seat out schema
class SeatOut(BaseModel):
    seat_id: int
    row: str
    number: str
    status: str
    price: int

    model_config = ConfigDict(from_attributes=True)
