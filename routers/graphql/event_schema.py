import strawberry
from typing import Optional, List
from datetime import date, time
from config.db import SessionLocal
from services.event_service import get_events, create_event, get_event_by_id
from schemas.graphql.event_type import EventInput
from schemas.graphql.shared_types import RoleEnum, ZoneType, DeaneryType
from services.event_service import EventDetailData
from strawberry.types import Info
from utils.auth_utils import get_current_user


# ── Types ──────────────────────────────────────────────────────────────────────

@strawberry.type
class EventCreatorType:
    id: int
    name: str


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
    zone_id: Optional[int]
    deanery_id: Optional[int]
    created_by: int
    creator: Optional[EventCreatorType]
    registered_parishes_count: int


@strawberry.type
class PaginatedEvents:
    events: List[EventType]
    total_count: int
    page: int
    total_pages: int


# ── Detail nested types ────────────────────────────────────────────────────────
@strawberry.type
class RegisteredParishType:
    id: int
    name: str
    created_at: Optional[date]
    attendance_status: Optional[str]       # "registered" | "attended" | "absent"
    deanery: Optional[DeaneryType]
    registered_by: Optional[EventCreatorType]


@strawberry.type
class EventDetailsType:
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

    # Resolved relations
    creator: Optional[EventCreatorType]
    zone: Optional[ZoneType]
    deanery: Optional[DeaneryType]

    # Counts
    registered_parishes_count: int
    total_parishes_in_scope: Optional[int]
    attended_parishes_count: int
    absent_parishes_count: int

    # Nested lists
    registered_parishes: List[RegisteredParishType]

    # Per-request: did the current user's parish already RSVP?
    my_parish_rsvpd: bool


# ── Filters ────────────────────────────────────────────────────────────────────

@strawberry.input
class EventFilters:
    search:     Optional[str]  = None
    scope:      Optional[str]  = None
    date_from:  Optional[date] = None
    date_to:    Optional[date] = None
    zone_id:    Optional[int]  = None
    deanery_id: Optional[int]  = None


# ── Permission check ───────────────────────────────────────────────────────────

def check_event_scope(user, input):
    scope = input.scope
    role  = getattr(user, "role", None)

    if hasattr(role,  "value"): role  = role.value
    if hasattr(scope, "value"): scope = scope.value

    role  = role.strip()
    scope = scope.strip()

    UNIVERSAL_ACCESS   = {"super_user", "ysc_chaplain", "ysc_coordinator", "adn_moderator"}
    SCOPE_RESTRICTIONS = {"deanery_moderator": "deanery", "zone_moderator": "zone"}
    NO_CREATE_ACCESS   = {"parish_member", "parish_moderator"}

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


# ── Queries ────────────────────────────────────────────────────────────────────

@strawberry.type
class EventQuery:

    @strawberry.field
    def events(
        self,
        info: Info,
        page:    int = 1,
        limit:   int = 10,
        filters: Optional[EventFilters] = None,
    ) -> PaginatedEvents:
        db   = SessionLocal()
        user = get_current_user(info)
        try:
            result = get_events(
                db,
                user=user,
                page=page,
                limit=limit,
                search=filters.search         if filters else None,
                scope=filters.scope           if filters else None,
                date_from=filters.date_from   if filters else None,
                date_to=filters.date_to       if filters else None,
                zone_id=filters.zone_id       if filters else None,
                deanery_id=filters.deanery_id if filters else None,
            )
            return PaginatedEvents(
                events=result["events"],
                total_count=result["total_count"],
                page=page,
                total_pages=-(-result["total_count"] // limit),
            )
        finally:
            db.close()

    @strawberry.field
    def event(self, info: Info, id: int) -> Optional[EventDetailsType]:
        db   = SessionLocal()
        user = get_current_user(info)
        try:
            return get_event_by_id(db, event_id=id, current_user=user)
        finally:
            db.close()


# ── Mutation ───────────────────────────────────────────────────────────────────

@strawberry.type
class EventMutation:

    @strawberry.mutation
    def create_event(self, info: Info, input: EventInput) -> EventType:
        db   = SessionLocal()
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