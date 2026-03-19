# services/event_service.py
from sqlalchemy.orm import Session
from models.event import Event

def get_events(db: Session):
    return db.query(Event).all()

def get_event_by_id(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()

def create_event(db: Session, title: str, description: str, charges, days: int, event_date, start_time, end_time, scope: str, created_by: int, zone_id: int = None, deanery_id: int = None):
    if not title.strip():
        raise Exception("Title is required")

    if end_time <= start_time:
        raise Exception("End time must be after start time")

    if charges < 0:
        raise Exception("Charges cannot be negative")

    if days < 1:
        raise Exception("Days must be at least 1")

    if scope == "zone" and not zone_id:
        raise Exception("Zone id is required for zone events")

    if scope == "deanery" and not deanery_id:
        raise Exception("Deanery id is required for deanery events")

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