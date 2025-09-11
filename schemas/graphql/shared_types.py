from __future__ import annotations
import strawberry
import enum
from .outstation_type import OutstationType
from typing import List, Optional
import datetime

@strawberry.type
class ZoneType:
    id: int
    name: str
    deaneries: List[DeaneryType]

@strawberry.type
class DeaneryType:
    id: int
    name: str
    zone:  ZoneType
    parishes: List[ParishType]

@strawberry.type
class ParishType:
    id: int
    name: str
    deanery: DeaneryType
    outstations: List[OutstationType]
    users: List[UserType] = None

@strawberry.enum
class RoleEnum(enum.Enum):
    parish_member = "parish_member"
    parish_moderator = "parish_moderator"
    deanery_moderator = "deanery_moderator"
    ysc_coordinator = "ysc_coordinator"
    ysc_chaplain = "ysc_chaplain"
    super_user = "super_user"

@strawberry.enum
class UserStatus(enum.Enum):
    active_member = "Active"
    archived_member = "Archived"
    transitioned_member = "Transitioned"

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
    status: UserStatus
    profile_pic: Optional[str] = None
    parish: ParishType = None
