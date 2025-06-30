import strawberry

@strawberry.type
class UserType:
    id: int
    name: str
    email: str
    phonenumber: str

@strawberry.input
class UserInput:
    name: str
    email: str
    phonenumber: str
    password: str

@strawberry.input
class UpdateUserInput:
    id: int
    name: str
    email: str
    phonenumber: str
    password: str

@strawberry.input
class RegisterInput:
    name: str
    email: str
    phonenumber: str
    password: str

@strawberry.input
class LoginInput:
    email: str
    password: str

@strawberry.type
class TokenType:
    access_token: str
    token_type: str