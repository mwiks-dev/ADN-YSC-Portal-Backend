from dataclasses import dataclass, field
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


# ── Dataclasses returned by get_event_by_id ───────────────────────────────────
# Strawberry serializes plain dataclasses cleanly; avoids dynamic attribute
# assignment on SQLAlchemy ORM objects which Strawberry cannot introspect.

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

DEANERY_RESTRICTED_ROLES = {"parish_member", "parish_moderator", "deanery_moderator"}
ZONE_RESTRICTED_ROLES    = {"zone_moderator"}


def _resolve_role(user) -> str:
    role = getattr(user, "role", None)
    return role.value.strip() if hasattr(role, "value") else str(role).strip()


def _apply_visibility_filter(query, db, user):
    """Auto-scopes event visibility by role. Always applied before user-supplied filters."""
    role = _resolve_role(user)

    if role in DEANERY_RESTRICTED_ROLES:
        parish = db.query(Parish).filter(Parish.id == user.parish_id).first()
        if not parish:
            return query.filter(False)
        return query.filter(Event.deanery_id == parish.deanery_id)

    if role in ZONE_RESTRICTED_ROLES:
        deanery_ids = [
            d[0] for d in db.query(Parish.deanery_id)
            .filter(Parish.zone_id == user.zone_id)
            .distinct().all()
            if d[0] is not None
        ]
        return query.filter(
            (Event.zone_id == user.zone_id) |
            (Event.deanery_id.in_(deanery_ids))
        )

    return query  # universal roles — no restriction


def get_event_by_id(db: Session, event_id: int, current_user=None) -> EventDetailData | None:
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        return None

    # ── Creator ────────────────────────────────────────────────────────────────
    creator_row = db.query(User).filter(User.id == event.created_by).first()
    creator     = CreatorData(id=creator_row.id, name=creator_row.name) if creator_row else None

    # ── Zone & Deanery ─────────────────────────────────────────────────────────
    zone_row    = db.query(Zone).filter(Zone.id == event.zone_id).first()         if event.zone_id    else None
    deanery_row = db.query(Deanery).filter(Deanery.id == event.deanery_id).first() if event.deanery_id else None
    zone        = ZoneData(id=zone_row.id, name=zone_row.name)         if zone_row    else None
    deanery     = DeaneryData(id=deanery_row.id, name=deanery_row.name) if deanery_row else None

    # ── Registrations ──────────────────────────────────────────────────────────
    registrations = (
        db.query(EventParishRegistration)
        .filter(EventParishRegistration.event_id == event_id)
        .all()
    )

    registered_parishes = []
    for reg in registrations:
        parish_row = db.query(Parish).filter(Parish.id == reg.parish_id).first()
        if not parish_row:
            continue

        parish_deanery_row = db.query(Deanery).filter(Deanery.id == parish_row.deanery_id).first()
        reg_by_row         = db.query(User).filter(User.id == reg.registered_by).first() if reg.registered_by else None

        registered_parishes.append(RegisteredParishData(
            id                = parish_row.id,
            name              = parish_row.name,
            created_at        = reg.created_at,
            attendance_status = reg.attendance_status,
            deanery           = DeaneryData(id=parish_deanery_row.id, name=parish_deanery_row.name) if parish_deanery_row else None,
            registered_by     = CreatorData(id=reg_by_row.id, name=reg_by_row.name) if reg_by_row else None,
        ))

    # ── Counts ─────────────────────────────────────────────────────────────────
    attended = sum(1 for p in registered_parishes if p.attendance_status == "attended")
    absent   = sum(1 for p in registered_parishes if p.attendance_status == "absent")

    # ── Total parishes in scope ────────────────────────────────────────────────
    scope_str   = event.scope.value if hasattr(event.scope, "value") else event.scope
    scope_query = db.query(func.count(Parish.id))
    if scope_str == "deanery" and event.deanery_id:
        scope_query = scope_query.filter(Parish.deanery_id == event.deanery_id)
    elif scope_str == "zone" and event.zone_id:
        scope_query = scope_query.filter(Parish.zone_id == event.zone_id)
    total_in_scope = scope_query.scalar()

    # ── RSVP flag ──────────────────────────────────────────────────────────────
    current_parish_id = getattr(current_user, "parish_id", None)
    my_parish_rsvpd   = any(r.parish_id == current_parish_id for r in registrations) if current_parish_id else False

    return EventDetailData(
        id                       = event.id,
        title                    = event.title,
        description              = event.description,
        charges                  = float(event.charges),
        days                     = event.days,
        event_date               = event.event_date,
        start_time               = event.start_time,
        end_time                 = event.end_time,
        scope                    = scope_str,
        rsvp_deadline            = getattr(event, "rsvp_deadline", None),
        creator                  = creator,
        zone                     = zone,
        deanery                  = deanery,
        registered_parishes_count = len(registered_parishes),
        total_parishes_in_scope  = total_in_scope,
        attended_parishes_count  = attended,
        absent_parishes_count    = absent,
        registered_parishes      = registered_parishes,
        my_parish_rsvpd          = my_parish_rsvpd,
    )


def get_events(db: Session, user, page=1, limit=10, search=None, scope=None,
               date_from=None, date_to=None, zone_id=None, deanery_id=None):

    query = db.query(Event)

    # 1. Visibility gate — always first so it cannot be bypassed by user filters
    query = _apply_visibility_filter(query, db, user)

    # 2. User-supplied filters
    if search:     query = query.filter(Event.title.ilike(f"%{search}%"))
    if scope:      query = query.filter(Event.scope == scope)
    if date_from:  query = query.filter(Event.event_date >= date_from)
    if date_to:    query = query.filter(Event.event_date <= date_to)
    if zone_id:    query = query.filter(Event.zone_id == zone_id)
    if deanery_id: query = query.filter(Event.deanery_id == deanery_id)

    total_count = query.count()
    events = (
        query.order_by(Event.event_date.asc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    # Attach derived fields — consider a dataloader if event lists grow large
    for event in events:
        event.creator = db.query(User).filter(User.id == event.created_by).first()
        event.registered_parishes_count = (
            db.query(func.count(EventParishRegistration.id))
            .filter(EventParishRegistration.event_id == event.id)
            .scalar()
        )

    return {"events": events, "total_count": total_count}


def create_event(db: Session, title: str, description: str, charges, days: int,
                 event_date, start_time, end_time, scope: str, created_by: int,
                 zone_id: int = None, deanery_id: int = None):

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
        title=title, description=description, charges=charges, days=days,
        event_date=event_date, start_time=start_time, end_time=end_time,
        scope=scope, created_by=created_by, zone_id=zone_id, deanery_id=deanery_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event