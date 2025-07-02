import strawberry
from .parish_type import ParishType
import enum

@strawberry.enum
class RoleEnum(enum.Enum):
    parish_member = "parish_member"
    parish_moderator = "parish_moderator"
    deanery_moderator = "deanery_moderator"
    ysc_coordinator = "ysc_coordinator"
    ysc_chaplain = "ysc_chaplain"

@strawberry.type
class UserType:
    id: int
    name: str
    email: str
    phonenumber: str
    role: RoleEnum
    parish: ParishType

@strawberry.input
class UserInput:
    name: str
    email: str
    phonenumber: str
    password: str
    role: RoleEnum
    parish_id: int

@strawberry.input
class UpdateUserInput:
    id: int
    name: str
    email: str
    phonenumber: str
    password: str
    role: RoleEnum
    parish_id: int

@strawberry.input
class RegisterInput:
    name: str
    email: str
    phonenumber: str
    password: str
    role: RoleEnum 
    parish_id: int

@strawberry.input
class LoginInput:
    email: str
    password: str

@strawberry.type
class TokenType:
    access_token: str
    token_type: str

@strawberry.input
class ResetPasswordInput:
    email: str
    old_password: str
    new_password: str