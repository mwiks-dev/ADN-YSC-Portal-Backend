# services/event_service.py
from sqlalchemy.orm import Session
from models.event import Event

def get_events(db: Session):
    return db.query(Event).all()

def get_event_by_id(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()

def create_event(
    db: Session,
    title: str,
    description: str,
    charges,
    days: int,
    event_date,
    start_time,
    end_time,
    scope: str,
    created_by: int,
    zone_id: int = None,
    deanery_id: int = None
):
    event = Event(
        title=title,
        description=description,
        charges=charges,
        days=days,
        event_date=event_date,
        start_time=start_time,
        end_time=end_time,
        scope=scope,
        created_by=created_by,
        zone_id=zone_id,
        deanery_id=deanery_id
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event