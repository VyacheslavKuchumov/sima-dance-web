from sqlalchemy.orm import Session
from app.models.events import Event
from app.schemas.events import EventCreate, EventUpdate




# function for getting unarchived events ASC
def get_events(db: Session):
    return db.query(Event).filter(Event.archived == False).order_by(Event.event_date).all()

# function for getting archived events DESC
def get_archived_events(db: Session):
    return db.query(Event).filter(Event.archived == True).order_by(Event.event_date.desc()).all()



# function for creating a new event
def create_event(db: Session, event: EventCreate):
    db_event = Event(
        event_name=event.event_name,
        event_date=event.event_date,
        img_url=event.img_url
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


# function for updating an existing event by id
def update_event(db: Session, event_id: int, event: EventUpdate):
    db_event = db.query(Event).filter(Event.event_id == event_id).first()
    db_event.event_name = event.event_name
    db_event.event_date = event.event_date
    db_event.img_url = event.img_url
    db_event.archived = event.archived
    db.commit()
    db.refresh(db_event)
    return db_event


# function for deleting an existing event by id
def delete_event(db: Session, event_id: int):
    event = db.query(Event).filter(Event.event_id == event_id).first()
    db.delete(event)
    db.commit()
    return event





