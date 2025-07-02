import strawberry


@strawberry.input
class ParishInput:
    name: str
    deanery_id: int
    deanery_name: str

@strawberry.input
class UpdateParishDetails:
    id: int
    name: str


