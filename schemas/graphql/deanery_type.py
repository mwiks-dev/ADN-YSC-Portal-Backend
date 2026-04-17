import strawberry
from typing import List, Optional
from .shared_types import DeaneryType

@strawberry.input
class DeaneryInput:
    name: str
    zone_id: int
    parishes: Optional[List[str]] = None
 
@strawberry.input
class UpdateDeaneryDetails:
    id: int
    name: str
    zone_id: int

@strawberry.input
class DeanerySearchInput:
    search: Optional[str] = ""
    page: Optional[int] = 1
    limit: Optional[int] = 10
    zone_id: Optional[int] = None

@strawberry.type
class DeaneryListResponse:
    deaneries: List[DeaneryType]
    totalCount: int

@strawberry.type
class CreateDeaneryResponse:
    message: str
    deanery: DeaneryType
    