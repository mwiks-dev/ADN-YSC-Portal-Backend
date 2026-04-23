import strawberry
from typing import Optional, List
from datetime import date, time
from schemas.graphql.event_parish_type import EventParishRegistrationType

@strawberry.input
class EventInput:
    title: str
    description: str
    charges: float
    days: int
    event_date: date
    start_time: time
    end_time: time
    scope: str
    zone_id: Optional[int] = None
    deanery_id: Optional[int] = None
    
@strawberry.input
class RegisterEventInput:
    event_id: int
    parish_id: int
    number_of_participants: int

