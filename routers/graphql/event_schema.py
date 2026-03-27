import strawberry
from typing import Optional, List
from datetime import date, time
from config.db import SessionLocal
from services.event_service import get_events, create_event
from schemas.graphql.event_type import EventInput
from schemas.graphql.shared_types import RoleEnum
from strawberry.types import Info
from utils.auth_utils import is_chaplain, is_ysc_coordinator, can_register_users, is_superuser, get_current_user


@strawberry.type
class EventType:
    id: int
    title: str
    description: str
    charges: float
    days: int
    event_date: date
    start_time: time
    end_time: time
    scope: str
    created_by: int
    zone_id: Optional[int]
    deanery_id: Optional[int]


# Check if user can create events
def check_event_scope(user, input):
    scope = input.scope
    role = getattr(user, "role", None)

    if hasattr(role, "value"):
        role = role.value
    if hasattr(scope, "value"):
        scope = scope.value

    role = role.strip()
    scope = scope.strip()

    UNIVERSAL_ACCESS = {"super_user", "ysc_chaplain", "ysc_coordinator", "adn_moderator"}
    SCOPE_RESTRICTIONS = {"deanery_moderator": "deanery", "zone_moderator": "zone"}
    NO_CREATE_ACCESS = {"parish_member", "parish_moderator"}

    if role in NO_CREATE_ACCESS:
        raise PermissionError(f"Role '{role}' is not permitted to create events.")

    if role in UNIVERSAL_ACCESS:
        return True

    if role in SCOPE_RESTRICTIONS:
        allowed_scope = SCOPE_RESTRICTIONS[role]
        if scope != allowed_scope:
            raise PermissionError(
                f"Role '{role}' can only create events with scope '{allowed_scope}', got '{scope}'."
            )
        return True

    raise PermissionError(f"Unrecognized role '{role}'.")

@strawberry.type
class EventQuery:
    @strawberry.field
    def events(self) -> List[EventType]:
        db = SessionLocal()
        try:
            return get_events(db)
        finally:
            db.close()


@strawberry.type
class EventMutation:
    @strawberry.mutation
    def create_event(self, info: Info, input: EventInput) -> EventType:
        db = SessionLocal()
        user = get_current_user(info)

        check_event_scope(user, input)

        try:
            return create_event(
                db,
                title=input.title,
                description=input.description,
                charges=input.charges,
                days=input.days,
                event_date=input.event_date,
                start_time=input.start_time,
                end_time=input.end_time,
                scope=input.scope,
                created_by=user.id,
                zone_id=input.zone_id,
                deanery_id=input.deanery_id,
            )
        finally:
            db.close()