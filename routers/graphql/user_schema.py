import strawberry
from typing import List, Optional
from config.db import SessionLocal
from schemas.graphql.user_type import UserType, UserInput, UpdateUserInput
from services.user_service import get_user_by_id, get_users, create_user, update_user, delete_user

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: int) -> Optional[UserType]:
        db = SessionLocal()
        return get_user_by_id(db, id)

    @strawberry.field
    def users(self) -> List[UserType]:
        db = SessionLocal()
        return get_users(db)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, input: UserInput) -> UserType:
        db = SessionLocal()
        return create_user(db, input.name, input.email, input.phonenumber, input.password)

    @strawberry.mutation
    def update_user(self, input: UpdateUserInput) -> Optional[UserType]:
        db = SessionLocal()
        return update_user(db, input.id, input.name, input.email, input.phonenumber, input.password)

    @strawberry.mutation
    def delete_user(self, id: int) -> Optional[UserType]:
        db = SessionLocal()
        return delete_user(db, id)

schema = strawberry.Schema(query=Query, mutation=Mutation)
