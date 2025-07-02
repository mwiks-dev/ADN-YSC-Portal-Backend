import strawberry
from .shared_types import RoleEnum

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