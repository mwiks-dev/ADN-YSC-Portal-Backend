from sqlalchemy.orm import Session
from sqlalchemy import func
from models.event import Event
from models.user import User
from models.parish import Parish
from models.event_parish_registration import EventParishRegistration

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
            return query.filter(False)  # no parish attached — return nothing
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


def get_event_by_id(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()


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