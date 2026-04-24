from __future__ import annotations
import strawberry
from strawberry.types import Info
from typing import Optional, List
from datetime import datetime, timezone, time
from sqlalchemy.orm import joinedload


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
from schemas.graphql.event_parish_type import EventParishRegistrationType,AdmitParishInput,AdmitParishResponse, EventParishRegistrationList
from schemas.graphql.shared_types import EventMiniType, ParishMiniType, UserMiniType

@strawberry.type
class EventParishRegistrationQuery:
    @strawberry.field
    def event_parish_registrations(
        self,
        info: Info,
        event_id: Optional[int] = None,
        parish_id: Optional[int] = None,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> EventParishRegistrationList:
    
        current_user = get_current_user(info)
        if not current_user:
            raise Exception("Unauthorized")

        db = SessionLocal()
        try:
            registrations, total = get_event_parish_registrations(
                db=db,
                event_id=event_id,
                parish_id=parish_id,
                page=page,
                limit=limit,
                search=search,
            )

            return EventParishRegistrationList(
                items=[map_registration_to_type(r) for r in registrations],
                total_count=total,
            )

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
            db.commit()
            return map_registration_to_type(registration)
        except Exception as e:
            db.rollback()
            raise e
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
            

def map_registration_to_type(reg):
    return EventParishRegistrationType(
        id=reg.id,

        event=EventMiniType(
            id=reg.event.id,
            title=reg.event.title,
            event_date=reg.event.event_date,
            start_time=reg.event.start_time,
            end_time=reg.event.end_time,
            scope=reg.event.scope,
        ) if reg.event else None,

        parish=ParishMiniType(
            id=reg.parish.id,
            name=reg.parish.name,
        ) if reg.parish else None,

        arrival_time=reg.arrival_time,
        number_of_participants=reg.number_of_participants,
        attendance_status=reg.attendance_status,
        is_cleared=reg.is_cleared,
        clearance_note=reg.clearance_note,
        fine_amount=reg.fine_amount,
        created_at=reg.created_at,

        registered_by=UserMiniType(
            id=reg.registrar.id,
            name=reg.registrar.name,
        ) if reg.registrar else None,

        cleared_by=UserMiniType(
            id=reg.clearer.id,
            name=reg.clearer.name,
        ) if reg.clearer else None,

        admitted_by=UserMiniType(
            id=reg.admitter.id,
            name=reg.admitter.name,
        ) if reg.admitter else None,
    )