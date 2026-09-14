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

@strawberry.input
class NewDeaneryInput:
    name: str
    zone_id: Optional[int] = None  # defaults to the source deanery's zone if omitted

@strawberry.input
class ParishAssignmentInput:
    parish_id: int
    target: str  # "A" -> deanery_a, "B" -> deanery_b

@strawberry.input
class SplitDeaneryInput:
    deanery_id: int
    deanery_a: NewDeaneryInput
    deanery_b: NewDeaneryInput
    parish_assignments: List[ParishAssignmentInput]
    delete_original: Optional[bool] = False

@strawberry.type
class SplitDeaneryResponse:
    message: str
    deanery_a: DeaneryType
    deanery_b: DeaneryType