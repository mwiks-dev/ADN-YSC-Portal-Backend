import strawberry
from .deanery_type import DeaneryType
from .outstation_type import OutstationType

@strawberry.type
class ParishType:
    id: int
    name: str
    deanery: DeaneryType
    outstations: list[OutstationType]

@strawberry.input
class UpdateParishDetails:
    id: int
    name: str

@strawberry.input
class ParishInput:
    name:str
