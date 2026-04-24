from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from models.event_parish_registration import EventParishRegistration
from models.user import User
from models.parish import Parish
from models.event import Event

from schemas.graphql.event_parish_type import AdmitParishInput
from utils.auth_utils import can_register_users


def get_event_parish_registration_by_id(db: Session, registration_id: int):
    return (
        db.query(EventParishRegistration)
        .filter(EventParishRegistration.id == registration_id)
        .first()
    )

def get_event_parish_registrations(
    db: Session,
    event_id: int = None,
    parish_id: int = None,
    page: int = 1,
    limit: int = 10,
    search: str = None,
):
    query = (
        db.query(EventParishRegistration)
        .options(
            joinedload(EventParishRegistration.event),
            joinedload(EventParishRegistration.parish),
            joinedload(EventParishRegistration.registrar),
            joinedload(EventParishRegistration.clearer),
            joinedload(EventParishRegistration.admitter),
        )
    )

    # filters
    if event_id is not None:
        query = query.filter(EventParishRegistration.event_id == event_id)

    if parish_id is not None:
        query = query.filter(EventParishRegistration.parish_id == parish_id)

    if search:
        query = query.join(EventParishRegistration.parish).filter(
            Parish.name.ilike(f"%{search}%")
        )

    # total BEFORE pagination
    total = query.count()

    # pagination
    registrations = (
        query.order_by(EventParishRegistration.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return registrations, total


def register_parish_for_event(
    db: Session,
    current_user: User,
    event_id: int,
    parish_id: int,
    number_of_participants: int
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

    registration = EventParishRegistration(
        event_id=event_id,
        parish_id=parish_id,
        arrival_time=None,          # ✅ not yet admitted — set only on admission
        number_of_participants=number_of_participants,
        is_cleared=True,
        clearance_note=None,
        registered_by=db_user.id,
        cleared_by=None,
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


def admit_parish_to_event(
    db: Session,
    current_user: User,
    input: AdmitParishInput
):
    if not current_user:
        raise Exception("Unauthorized")

    input = AdmitParishInput(**input.__dict__)

    registration = get_event_parish_registration_by_id(db, input.registration_id)
    if not registration:
        raise Exception("Registration not found.")

    event = db.query(Event).filter(Event.id == registration.event_id).first()
    if not event:
        raise Exception("Event not found.")

    parish = db.query(Parish).filter(Parish.id == registration.parish_id).first()
    if not parish:
        raise Exception("Parish not found.")

    # ✅ Already admitted check — after parish is loaded so we can use parish.name
    if registration.arrival_time is not None:
        raise Exception(f"{parish.name} has already been admitted to this event.")

    allowed, reason = can_admit_parish_to_event(db, current_user, event, parish)
    if not allowed:
        print(
            f"User {current_user.id} denied admitting parish {parish.id} "
            f"to event {event.id}: {reason}"
        )
        raise Exception(reason)

    try:
        # ── Time check ────────────────────────────────────────────────────
        now = datetime.now()
        is_late = event.start_time and now.time() > event.start_time

        if not is_late:
            # On time — auto-clear, no fine
            registration.is_cleared = True
            registration.fine_amount = 0
            registration.clearance_note = None
            registration.cleared_by = None

        else:
            # Late — fine or waiver required
            if input.fine_amount and input.fine_amount > 0:
                registration.is_cleared = False
                registration.fine_amount = input.fine_amount
                registration.clearance_note = None
                registration.cleared_by = None

            elif input.clearance_note and input.clearance_note.strip():
                registration.is_cleared = True
                registration.fine_amount = 0
                registration.clearance_note = input.clearance_note.strip()
                registration.cleared_by = current_user.id

            else:
                raise Exception(
                    "Parish is arriving late. Either provide a fine amount or a "
                    "clearance note explaining why no fine was applied."
                )

        registration.number_of_participants = input.number_of_participants
        registration.arrival_time = now       # ✅ stamp admission time
        registration.admitted_by = current_user.id

        db.commit()
        db.refresh(registration)
        return registration

    except Exception as e:
        db.rollback()
        raise e


def can_admit_parish_to_event(
    db: Session,
    current_user: User,
    event: Event,
    parish: Parish
) -> tuple[bool, str]:

    if not current_user:
        return False, "Unauthorized user."

    if current_user.parish_id == parish.id:
        return False, "You cannot admit your own parish."

    GLOBAL_SCOPE = ["ysc_coordinator", "ysc_chaplain", "super_user"]
    if current_user.role in GLOBAL_SCOPE:
        return True, "Allowed: global role."

    event_scope = event.scope

    if event_scope == "zone":
        if current_user.role != "zone_moderator":
            return False, "Only zone moderators can admit parishes to zone events."
        return True, "Allowed: zone moderator."

    if event_scope == "deanery":
        if current_user.role != "deanery_moderator":
            return False, "Only deanery moderators can admit parishes to deanery events."
        return True, "Allowed: deanery moderator."

    return False, f"Unsupported or restricted event scope: {event_scope}."