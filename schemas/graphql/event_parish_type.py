import strawberry
from typing import Optional
from datetime import datetime

from schemas.graphql.shared_types import EventMiniType, ParishMiniType, UserMiniType

@strawberry.type
class EventParishRegistrationType:
    id: int
    event: EventMiniType
    parish: ParishMiniType

    arrival_time: Optional[datetime]
    number_of_participants: int
    attendance_status: Optional[str]
    is_cleared: bool
    clearance_note: Optional[str]
    fine_amount: float
    created_at: datetime

    registered_by: Optional[UserMiniType]
    cleared_by: Optional[UserMiniType]
    admitted_by: Optional[UserMiniType]
    
@strawberry.type
class EventParishRegistrationList:
    items: list["EventParishRegistrationType"]
    total_count: int

@strawberry.input
class AdmitParishInput:
    registration_id: int
    fine_amount: float
    number_of_participants: int
    clearance_note: Optional[str] = None

@strawberry.type
class AdmitParishResponse:
    message: str
    registration: EventParishRegistrationType