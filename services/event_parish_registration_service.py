from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from models.event_parish_registration import EventParishRegistration
from models.user import User
from models.parish import Parish

from utils.auth_utils import can_register_users

def get_event_parish_registration_by_id(db: Session, registration_id: int):
    return (
        db.query(EventParishRegistration)
        .filter(EventParishRegistration.id == registration_id)
        .first()
    )

def get_event_parish_registrations(db: Session, event_id: int = None, parish_id: int = None):
    query = db.query(EventParishRegistration).order_by(EventParishRegistration.id.desc())

    if event_id is not None:
        query = query.filter(EventParishRegistration.event_id == event_id)

    if parish_id is not None:
        query = query.filter(EventParishRegistration.parish_id == parish_id)

    return query.all()


def register_parish_for_event(
    db: Session,
    current_user: User,
    event_id: int,
    parish_id: int,
    number_of_participants: int,
    is_cleared: bool = True,
    clearance_note: str = None,
):
    if not current_user:
        raise Exception("Unauthorized")

    db_user = (
        db.query(User)
        .options(joinedload(User.parish))
        .filter(User.id == current_user.id)
        .first()
    )

    if not db_user:
        raise Exception("User not found.")

    if not can_register_users(db_user):
        raise Exception("You are not allowed to register a parish for an event.")

    if number_of_participants < 1:
        raise Exception("Number of participants must be at least 1.")

    parish = db.query(Parish).filter(Parish.id == parish_id).first()
    if not parish:
        raise Exception("Parish not found.")

    if db_user.parish is None:
        raise Exception("Current user is not attached to a parish.")

    # if db_user.parish.deanery_id != parish.deanery_id:
    #     raise Exception("You can only register parishes within your deanery.")

    existing = (
        db.query(EventParishRegistration)
        .filter(
            EventParishRegistration.event_id == event_id,
            EventParishRegistration.parish_id == parish_id,
        )
        .first()
    )

    if existing:
        raise Exception("This parish is already registered for this event.")

    final_is_cleared = True if not clearance_note else is_cleared

    registration = EventParishRegistration(
        event_id=event_id,
        parish_id=parish_id,
        arrival_time=datetime.utcnow(),
        number_of_participants=number_of_participants,
        is_cleared=final_is_cleared,
        clearance_note=clearance_note,
        registered_by=db_user.id,
        cleared_by=db_user.id if final_is_cleared else None,
    )

    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration


def clear_event_parish_registration(
    db: Session,
    current_user: User,
    registration_id: int,
    is_cleared: bool,
    clearance_note: str = None,
):
    if not current_user:
        raise Exception("Unauthorized")

    registration = get_event_parish_registration_by_id(db, registration_id)
    if not registration:
        raise Exception("Registration not found.")

    registration.is_cleared = is_cleared
    registration.clearance_note = clearance_note
    registration.cleared_by = current_user.id

    db.commit()
    db.refresh(registration)
    return registration