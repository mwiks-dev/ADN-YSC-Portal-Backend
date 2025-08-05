from __future__ import annotations
import strawberry
import enum
from .deanery_type import DeaneryType
from .outstation_type import OutstationType
from typing import List
import datetime

@strawberry.type
class ParishType:
    id: int
    name: str
    deanery: DeaneryType
    outstations: list[OutstationType]
    users: List[UserType] = None

@strawberry.enum
class RoleEnum(enum.Enum):
    parish_member = "parish_member"
    parish_moderator = "parish_moderator"
    deanery_moderator = "deanery_moderator"
    ysc_coordinator = "ysc_coordinator"
    ysc_chaplain = "ysc_chaplain"
    super_user = "super_user"


@strawberry.type
class UserType:
    id: int
    name: str
    email: str
    phonenumber: str
    dateofbirth: datetime.date
    idnumber: int
    baptismref: str
    role: RoleEnum
    parish: ParishType = None