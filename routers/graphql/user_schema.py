import strawberry
from strawberry.types import Info
from typing import List, Optional
from config.db import SessionLocal
from routers.graphql.parish_schema import ParishQuery,ParishMutation
from schemas.graphql.user_type import UserType, UserInput, UpdateUserInput, RegisterInput, LoginInput, TokenType
from services.user_service import get_user_by_id, get_user_by_email, get_users, create_user, update_user, delete_user, authenticate_user, create_access_token, verify_token

def get_current_user(info: Info) -> Optional[UserType]:
    auth_header = info.context.get("request").headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    email = verify_token(token)
    if not email:
        return None
    db = SessionLocal()
    user = get_user_by_email(db, email)
    if not user:
        return None
    return UserType(id=user.id, name=user.name, email=user.email, phonenumber=user.phonenumber)

@strawberry.type
class Query(ParishQuery):
    @strawberry.field
    def user(self, info: Info, id: int) -> Optional[UserType]:
        if not get_current_user(info):
            raise Exception("Unauthorized")
        db = SessionLocal()
        return get_user_by_id(db, id)

    @strawberry.field
    def users(self, info: Info) -> List[UserType]:
        if not get_current_user(info):
            raise Exception("Unauthorized")
        db = SessionLocal()
        return get_users(db)
    
@strawberry.type
class Mutation(ParishMutation):
    @strawberry.mutation
    def create_user(self, input: UserInput) -> UserType:
        db = SessionLocal()
        return create_user(db, input.name, input.email, input.phonenumber, input.password)

    @strawberry.mutation
    def update_user(self, info: Info, input: UpdateUserInput) -> Optional[UserType]:
        if not get_current_user(info):
            raise Exception("Unauthorized")
        db = SessionLocal()
        return update_user(db, input.id, input.name, input.email, input.phonenumber, input.password)

    @strawberry.mutation
    def delete_user(self, info: Info, id: int) -> Optional[UserType]:
        if not get_current_user(info):
            raise Exception("Unauthorized")
        db = SessionLocal()
        return delete_user(db, id)
    
    @strawberry.mutation
    def register(self, input:RegisterInput) -> UserType:
        db = SessionLocal()
        existing_user = get_user_by_email(db,input.email)
        if existing_user:
            raise Exception("User with this email already exists")
        return create_user(db,input.name, input.email, input.phonenumber,input.password )

    @strawberry.mutation
    def login(self, input: LoginInput) -> Optional[TokenType]:
        db = SessionLocal()
        user = authenticate_user(db, input.email, input.password)
        if not user:
            return None
        token = create_access_token(data={"sub": user.email})
        return TokenType(access_token=token, token_type="bearer")

schema = strawberry.Schema(query=Query, mutation=Mutation)
