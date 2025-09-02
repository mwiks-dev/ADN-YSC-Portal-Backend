from typing import List, Optional
import strawberry
from .shared_types import UserType,RoleEnum, UserStatus
import datetime

@strawberry.input
class UserInput:
    name: str
    email: str
    phonenumber: str
    dateofbirth: datetime.date
    idnumber: int
    baptismref: str
    password: str
    role: RoleEnum
    status: UserStatus
    profile_pic: Optional[str] 
    parish_id: int

@strawberry.input
class UpdateUserInput:
    id: int
    name: str
    email: str
    phonenumber: str
    dateofbirth: datetime.date
    idnumber: int
    baptismref: str
    password: str
    role: RoleEnum
    status: UserStatus
    parish_id: int

@strawberry.input
class RegisterInput:
    name: str
    email: str
    phonenumber: str
    dateofbirth: datetime.date
    idnumber: int
    baptismref: str
    password: str
    role: RoleEnum 
    status: UserStatus
    profile_pic: Optional[str] = strawberry.field(default=None)
    parish_id: int
    

@strawberry.input
class LoginInput:
    email: str
    password: str

@strawberry.input
class SearchInput:
    search: Optional[str] = ""
    page: Optional[int] = 1
    limit: Optional[int] = 10
    parish_id: Optional[int] = strawberry.field(default=None, name="parishId") 
@strawberry.type
class UserListResponse:
    users: List[UserType]
    totalCount: int

@strawberry.type
class TokenType:
    access_token: str
    token_type: str

@strawberry.input
class ResetPasswordInput:
    email: str
    old_password: str
    new_password: str

@strawberry.type
class LoginPayload:
    token: TokenType
    user: UserType