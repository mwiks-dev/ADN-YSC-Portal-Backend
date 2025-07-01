import strawberry
from typing import List
from schemas.graphql.user_type import UserType


@strawberry.type
class ParishType:
    id: int
    name: str
    deanery: str
    users:List[UserType]

@strawberry.input
class UpdateParishDetails:
    id: int
    name: str
    deanery: str

@strawberry.input
class ParishInput:
    name:str
    deanery:str
