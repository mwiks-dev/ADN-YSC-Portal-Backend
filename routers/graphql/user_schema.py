import strawberry
from strawberry.types import Info
from typing import List, Optional
from config.db import SessionLocal
from schemas.graphql.user_type import UserInput, UpdateUserInput, RegisterInput, LoginInput, TokenType, ResetPasswordInput
from schemas.graphql.shared_types import UserType
from services.user_service import get_user_by_id, get_user_by_email, get_users, create_user, update_user, delete_user, authenticate_user, create_access_token, verify_token, reset_password
from utils.auth_utils import is_authenticated, is_chaplain, is_ysc_coordinator, is_deanery_moderator, is_parish_moderator, is_parish_member, can_register_users
from passlib.context import CryptContext
from routers.graphql.parish_schema import ParishQuery,ParishMutation

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_current_user(info: Info) -> Optional[UserType]:
    auth_header = info.context.get("request").headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    email = verify_token(token)
    if not email:
        return None
    db = SessionLocal()
    return get_user_by_email(db, email)
    
@strawberry.type
class Query:
    @strawberry.field
    def user(self, info: Info, id: int) -> Optional[UserType]:
        if not get_current_user(info):
            raise Exception("Unauthorized")
        db = SessionLocal()
        return get_user_by_id(db, id)

    @strawberry.field
    def users(self, info: Info) -> List[UserType]:
        user = get_current_user(info)
        if not is_chaplain(user) or is_ysc_coordinator(user):
            raise Exception("Unauthorized: Only the Chaplain and Coordinators can view all users!")
        db = SessionLocal()
        return get_users(db)
    
@strawberry.type
class Mutation(ParishMutation):
    @strawberry.mutation
    def create_user(self, input: UserInput) -> UserType:
        db = SessionLocal()
        return create_user(db, input.name, input.email, input.phonenumber, input.role)

    @strawberry.mutation
    def update_user(self, info: Info, input: UpdateUserInput) -> Optional[UserType]:
        user = get_current_user(info)
        if not user:
            raise Exception("Unauthorized")
        if not is_chaplain(user) and user.id != input.id:
            raise Exception("You can only update your own information!")
        db = SessionLocal()
        return update_user(db, input.id, input.name, input.email, input.phonenumber, input.password, input.role)

    @strawberry.mutation
    def delete_user(self, info: Info, id: int) -> Optional[UserType]:
        user = get_current_user(info)
        if not is_chaplain(user) or is_ysc_coordinator(user):
            raise Exception("Unauthorized: Only the Chaplain and Coordinators can delete users!")
        db = SessionLocal()
        return delete_user(db, id)
    
    @strawberry.mutation
    def register(self, info:Info, input:RegisterInput) -> UserType:
        db = SessionLocal()
        existing_user = get_user_by_email(db,input.email)
        if existing_user:
            raise Exception("User with this email already exists")
        current_user = get_current_user(info)
        if not current_user:
            raise Exception("Unauthorized")
        if not can_register_users(current_user):
            raise Exception("Unauthorized: Only the Chaplain, Coordinators, Deanery or Parish Moderators can register members.")
        user = create_user(db,input.name, input.email, input.phonenumber, input.password, input.role, parish_id = input.parish_id )
        return UserType(id=user.id, name=user.name, email=user.email, phonenumber=user.phonenumber, role= user.role, parish=user.parish)

    @strawberry.mutation
    def login(self, input: LoginInput) -> Optional[TokenType]:
        db = SessionLocal()
        user = authenticate_user(db, input.email, input.password)
        if not user:
            return None
        token = create_access_token(data={"sub": user.email})
        return TokenType(access_token=token, token_type="bearer")
    
    @strawberry.mutation
    def reset_password(self, info:Info, input: ResetPasswordInput) -> UserType:
        user = get_current_user(info)
        if not user or user.email != input.email:
            raise Exception("Unauthorized: Token mismatch or invalid user")
        db = SessionLocal()
        db_user = get_user_by_email(db, input.email)
        if not db_user:
            raise Exception("User not found")
        if not pwd_context.verify(input.old_password, db_user.password):
            raise Exception("Old password is incorrect")

        db_user.password = pwd_context.hash(input.new_password)
        db.commit()
        db.refresh(db_user)
        return UserType(id=user.id,name=user.name,email=user.email,phonenumber=user.phonenumber,role=user.role)

schema = strawberry.Schema(query=Query, mutation=Mutation)
