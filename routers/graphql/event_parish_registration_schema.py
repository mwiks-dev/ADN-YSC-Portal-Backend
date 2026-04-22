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
    admit_parish_to_event
)

from models.event import Event
from schemas.graphql.event_type import RegisterEventInput
from schemas.graphql.event_parish_type import EventParishRegistrationType,AdmitParishInput,AdmitParishResponse
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

            registration = register_parish_for_event(
                db=db,
                current_user=current_user,
                event_id=input.event_id,
                parish_id=input.parish_id,
                number_of_participants=input.number_of_participants,
            )
            db.commit()
            return map_registration_to_type(registration)
        except Exception as e:
            db.rollback()
            raise e
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

    @strawberry.mutation
    def admit_parish_to_event(
        self,
        info: Info,
        input: AdmitParishInput,
    ) -> AdmitParishResponse:
        current_user = get_current_user(info)
        if not current_user:
            raise Exception("Unauthorized")

        db = SessionLocal()
        try:
            registration = admit_parish_to_event(
                db=db,
                current_user=current_user,
                input=input
            )
            db.commit()
            db.refresh(registration)

            return AdmitParishResponse(
                message="Parish admitted successfully",
                registration=map_registration_to_type(registration),
            )
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            

def map_registration_to_type(registration) -> EventParishRegistrationType:
    return EventParishRegistrationType(
        id=registration.id,
        event_id=registration.event_id,
        parish_id=registration.parish_id,
        parish_name=registration.parish.name if registration.parish else "",
        arrival_time=registration.arrival_time,
        number_of_participants=registration.number_of_participants,
        attendance_status=registration.attendance_status,
        is_cleared=registration.is_cleared,
        clearance_note=registration.clearance_note,
        registered_by=registration.registered_by,
        cleared_by=registration.cleared_by,
        created_at=registration.created_at,
    )