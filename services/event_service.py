from dataclasses import dataclass
from datetime import date, time
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.event import Event
from models.user import User
from models.parish import Parish
from models.deanery import Deanery
from models.zone import Zone
from models.event_parish_registration import EventParishRegistration


@dataclass
class CreatorData:
    id: int
    name: str


@dataclass
class ZoneData:
    id: int
    name: str


@dataclass
class DeaneryData:
    id: int
    name: str


@dataclass
class RegisteredParishData:
    id: int
    name: str
    created_at: Optional[date]
    attendance_status: Optional[str]
    deanery: Optional[DeaneryData]
    registered_by: Optional[CreatorData]
    number_of_participants: Optional[int]


@dataclass
class EventDetailData:
    id: int
    title: str
    description: Optional[str]
    charges: float
    days: int
    event_date: date
    start_time: time
    end_time: time
    scope: str
    rsvp_deadline: Optional[date]

    creator: Optional[CreatorData]
    zone: Optional[ZoneData]
    deanery: Optional[DeaneryData]

    registered_parishes_count: int
    total_parishes_in_scope: Optional[int]
    attended_parishes_count: int
    absent_parishes_count: int

    registered_parishes: List[RegisteredParishData]
    my_parish_rsvpd: bool



def _build_event_detail(db: Session, event: Event, current_user=None) -> EventDetailData:

    creator_row = db.query(User).filter(User.id == event.created_by).first()
    creator = CreatorData(creator_row.id, creator_row.name) if creator_row else None

    zone_row = db.query(Zone).filter(Zone.id == event.zone_id).first() if event.zone_id else None
    deanery_row = db.query(Deanery).filter(Deanery.id == event.deanery_id).first() if event.deanery_id else None

    zone = ZoneData(zone_row.id, zone_row.name) if zone_row else None
    deanery = DeaneryData(deanery_row.id, deanery_row.name) if deanery_row else None

    registrations = db.query(EventParishRegistration)\
        .filter(EventParishRegistration.event_id == event.id)\
        .all()

    registered_parishes = []

    for reg in registrations:
        parish = db.query(Parish).filter(Parish.id == reg.parish_id).first()
        if not parish:
            continue

        parish_deanery = db.query(Deanery).filter(Deanery.id == parish.deanery_id).first()
        reg_by = db.query(User).filter(User.id == reg.registered_by).first() if reg.registered_by else None

        registered_parishes.append(RegisteredParishData(
            id=parish.id,
            name=parish.name,
            created_at=reg.created_at,
            attendance_status=reg.attendance_status,
            deanery=DeaneryData(parish_deanery.id, parish_deanery.name) if parish_deanery else None,
            registered_by=CreatorData(reg_by.id, reg_by.name) if reg_by else None,
            number_of_participants=reg.number_of_participants
        ))

    attended = sum(1 for p in registered_parishes if p.attendance_status == "attended")
    absent = sum(1 for p in registered_parishes if p.attendance_status == "absent")

    scope_str = event.scope.value if hasattr(event.scope, "value") else event.scope
    scope_query = db.query(func.count(Parish.id))

    if scope_str == "deanery" and event.deanery_id:
        scope_query = scope_query.filter(Parish.deanery_id == event.deanery_id)

    elif scope_str == "zone" and event.zone_id:
        deanery_ids = [
            d[0] for d in db.query(Deanery.id)
            .filter(Deanery.zone_id == event.zone_id)
            .all()
        ]
        scope_query = scope_query.filter(Parish.deanery_id.in_(deanery_ids))

    total_in_scope = scope_query.scalar()

    current_parish_id = getattr(current_user, "parish_id", None)
    my_parish_rsvpd = any(r.parish_id == current_parish_id for r in registrations) if current_parish_id else False

    return EventDetailData(
        id=event.id,
        title=event.title,
        description=event.description,
        charges=float(event.charges),
        days=event.days,
        event_date=event.event_date,
        start_time=event.start_time,
        end_time=event.end_time,
        scope=scope_str,
        rsvp_deadline=getattr(event, "rsvp_deadline", None),

        creator=creator,
        zone=zone,
        deanery=deanery,

        registered_parishes_count=len(registered_parishes),
        total_parishes_in_scope=total_in_scope,
        attended_parishes_count=attended,
        absent_parishes_count=absent,

        registered_parishes=registered_parishes,
        my_parish_rsvpd=my_parish_rsvpd,
    )



def get_event_by_id(db: Session, event_id: int, current_user=None):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return None

    return _build_event_detail(db, event, current_user)


def get_events(db: Session, user, page=1, limit=10, **filters):
    query = db.query(Event)

    total_count = query.count()

    events = (
        query.order_by(Event.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "events": [_build_event_detail(db, e, user) for e in events],
        "total_count": total_count
    }


def create_event(db: Session, **data):
    event = Event(**data)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event