import strawberry
from typing import List, Optional
from .shared_types import ZoneType

@strawberry.input
class ZoneInput:
    name: str
    deaneries: Optional[List[str]] = None

@strawberry.input
class UpdateZoneDetails:
    id: int
    name: str

@strawberry.input
class ZoneSearchInput:
    search: Optional[str] = ""
    page: Optional[int] = 1
    limit: Optional[int] = 10

@strawberry.type
class ZoneListResponse:
    zones: List[ZoneType]
    totalCount: int

@strawberry.type
class CreateZoneResponse:
    message: str
    parish: ZoneType
