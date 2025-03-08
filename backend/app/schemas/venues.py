from pydantic import BaseModel, ConfigDict


# # Venues table
# class Venue(Base):
#     __tablename__ = 'venues'
#     venue_id = Column(BigInteger, primary_key=True)
#     venue_name = Column(String, nullable=False)
    
#     seat = relationship("Seat", back_populates="venue")


# venue create schema
class VenueCreate(BaseModel):
    venue_name: str
    
# venue update schema
class VenueUpdate(BaseModel):
    venue_name: str


# venue out schema
class VenueOut(BaseModel):
    venue_id: int
    venue_name: str
    
    model_config = ConfigDict(from_attributes=True)    