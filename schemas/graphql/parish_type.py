import strawberry
from typing import List, Optional

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


