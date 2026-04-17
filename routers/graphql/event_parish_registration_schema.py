import strawberry
from strawberry.types import Info
from typing import Optional, List
from datetime import datetime, timezone, time

from config.db import SessionLocal
from utils.auth_utils import get_current_user
from services.event_parish_registration_service import (
    get_event_parish_registrations,
    register_parish_for_event,
    clear_event_parish_registration,
)

from models.event import Event
from schemas.graphql.event_type import RegisterEventInput



@strawberry.type
class EventParishRegistrationType:
    id: int
    event_id: int
    parish_id: int
    parish_name: str
    arrival_time: datetime
    number_of_participants: int
    attendance_status: Optional[str]
    is_cleared: bool
    clearance_note: Optional[str]
    registered_by: int
    cleared_by: Optional[int]
    created_at: datetime


def map_registration_to_type(registration) -> EventParishRegistrationType:
    return EventParishRegistrationType(
        id=registration.id,
        event_id=registration.event_id,
        parish_id=registration.parish_id,
        parish_name=registration.parish.name if registration.parish else "",
        arrival_time=registration.arrival_time,
        number_of_participants=registration.number_of_participants,
        is_cleared=registration.is_cleared,
        clearance_note=registration.clearance_note,
        registered_by=registration.registered_by,
        cleared_by=registration.cleared_by,
        created_at=registration.created_at,
    )


@strawberry.type
class EventParishRegistrationQuery:
    @strawberry.field
    def event_parish_registrations(
        self,
        info: Info,
        event_id: Optional[int] = None,
        parish_id: Optional[int] = None,
    ) -> List[EventParishRegistrationType]:
        current_user = get_current_user(info)
        if not current_user:
            raise Exception("Unauthorized")

        db = SessionLocal()
        try:
            registrations = get_event_parish_registrations(
                db, event_id=event_id, parish_id=parish_id
            )
            return [map_registration_to_type(item) for item in registrations]
        finally:
            db.close()


@strawberry.type
class EventParishRegistrationMutation:
    @strawberry.mutation
    def register_parish_for_event(
        self,
        info: Info,
        input: RegisterEventInput,
    ) -> EventParishRegistrationType:
        current_user = get_current_user(info)
        if not current_user:
            raise Exception("Unauthorized")

        db = SessionLocal()
        try:
            event = db.query(Event).filter(Event.id == input.event_id).first()
            if not event:
                raise Exception(f"Event with id {input.event_id} not found")

            event_date = event.event_date
            event_start = event.start_time

            if event_date and event_start:
                registration_deadline = datetime.combine(
                    event_date,
                    event_start,
                    tzinfo=timezone.utc
                )
            else:
                registration_deadline = None

            now = datetime.now(timezone.utc)

            is_registration_late = (
                registration_deadline is not None and now > registration_deadline
            )

            if is_registration_late:
                resolved_is_cleared = False
            else:
                resolved_is_cleared = input.is_cleared if input.is_cleared is not None else True

            registration = register_parish_for_event(
                db=db,
                current_user=current_user,
                event_id=input.event_id,
                parish_id=input.parish_id,
                number_of_participants=input.number_of_participants,
                is_cleared=resolved_is_cleared,
                clearance_note=input.clearance_note,
            )
            return map_registration_to_type(registration)
        finally:
            db.close()

    @strawberry.mutation
    def clear_event_parish_registration(
        self,
        info: Info,
        registration_id: int,
        is_cleared: bool = True,
        clearance_note: Optional[str] = None,
    ) -> EventParishRegistrationType:
        current_user = get_current_user(info)
        if not current_user:
            raise Exception("Unauthorized")

        db = SessionLocal()
        try:
            registration = clear_event_parish_registration(
                db=db,
                current_user=current_user,
                registration_id=registration_id,
                is_cleared=is_cleared,
                clearance_note=clearance_note,
            )
            return map_registration_to_type(registration)
        finally:
            db.close()