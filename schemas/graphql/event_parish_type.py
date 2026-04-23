import strawberry
from typing import Optional
from datetime import datetime

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