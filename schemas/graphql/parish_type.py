import strawberry
from typing import List, Optional
from .shared_types import ParishType

@strawberry.input
class ParishInput:
    name: str
    deanery: str
    outstations: Optional[List[str]] = None
 
@strawberry.input
class UpdateParishDetails:
    id: int
    name: str
    deanery: str

# @strawberry.input
# class SearchInput:
#     search: Optional[str] = ""
#     page: Optional[int] = 1
#     limit: Optional[int] = 100

@strawberry.type
class ParishListResponse:
    parishes: List[ParishType]
    totalCount: int