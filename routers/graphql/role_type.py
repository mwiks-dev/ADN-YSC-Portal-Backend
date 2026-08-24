import strawberry
from typing import List

@strawberry.type
class PermissionType:
    id: int
    name: str
    description: str | None

@strawberry.type
class RoleType:
    id: int
    name: str
    description: str | None
    permissions: List[PermissionType]

@strawberry.input
class AssignPermissionInput:
    role_id: int
    permission_id: int