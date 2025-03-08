from sqlalchemy.orm import Session
from app.models.venues import Venue
from app.schemas.venues import VenueCreate, VenueUpdate

# # # Venues table
# # class Venue(Base):
# #     __tablename__ = 'venues'
# #     venue_id = Column(BigInteger, primary_key=True)
# #     venue_name = Column(String, nullable=False)
    
# #     seat = relationship("Seat", back_populates="venue")


# # venue create schema
# class VenueCreate(BaseModel):
#     venue_name: str
    
# # venue update schema
# class VenueUpdate(BaseModel):
#     venue_name: str


# # venue out schema
# class VenueOut(BaseModel):
#     venue_id: int
#     venue_name: str
    
#     model_config = ConfigDict(from_attributes=True)    

# function for getting all venues
def get_venues(db: Session):
    return db.query(Venue).order_by(Venue.venue_id).all()

# function for creating a new venue
def create_venue(db: Session, venue: VenueCreate):
    db_venue = Venue(
        venue_name=venue.venue_name,
    )
    db.add(db_venue)
    db.commit()
    db.refresh(db_venue)
    return db_venue

# function for updating an existing venue by id
def update_venue(db: Session, venue_id: int, venue: VenueUpdate):
    db_venue = db.query(Venue).filter(Venue.venue_id == venue_id).first()
    db_venue.venue_name = venue.venue_name
    db.commit()
    db.refresh(db_venue)
    return db_venue

# function for deleting an existing venue by id
def delete_venue(db: Session, venue_id: int):
    venue = db.query(Venue).filter(Venue.venue_id == venue_id).first()
    db.delete(venue)
    db.commit()
    return venue

