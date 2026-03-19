# routers/graphql/event_schema.py
import strawberry
from typing import Optional, List
from datetime import date, time
from config.db import SessionLocal
from services.event_service import get_events, create_event


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
    def create_event(
        self,
        title: str,
        description: str,
        charges: float,
        days: int,
        event_date: date,
        start_time: time,
        end_time: time,
        scope: str,
        created_by: int,
        zone_id: Optional[int] = None,
        deanery_id: Optional[int] = None,
    ) -> EventType:
        db = SessionLocal()
        try:
            return create_event(
                db,
                title=title,
                description=description,
                charges=charges,
                days=days,
                event_date=event_date,
                start_time=start_time,
                end_time=end_time,
                scope=scope,
                created_by=created_by,
                zone_id=zone_id,
                deanery_id=deanery_id,
            )
        finally:
            db.close()