import strawberry
from .deanery_type import DeaneryType

@strawberry.type
class ParishType:
    id: int
    name: str

@strawberry.input
class UpdateParishDetails:
    id: int
    name: str

@strawberry.input
class ParishInput:
    name:str
