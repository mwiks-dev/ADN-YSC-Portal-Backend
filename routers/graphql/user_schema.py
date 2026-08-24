import strawberry
from strawberry.types import Info
from strawberry.file_uploads import Upload
from typing import Optional
from sqlalchemy.orm import joinedload
from config.db import SessionLocal
from schemas.graphql.user_type import (
    UpdateUserInput, RegisterInput, LoginInput, TokenType, ResetPasswordInput,
    LoginPayload, SearchInput, UserListResponse, UploadProfilePicResponse,
    UpdateUserRoleInput, UpdateUserPasswordResponse
)
from schemas.graphql.shared_types import UserType, RoleEnum, UserStatus
from services.user_service import (
    get_user_by_id, get_user_by_email, get_user_by_identifier, create_user, update_user, delete_user,
    authenticate_user, create_access_token
)
from utils.auth_utils import get_current_user
from utils.permission_utils import user_has_permission, get_user_permission_names
from utils.scope_utils import can_manage_parish
from utils.password_utils import generate_default_password
from passlib.context import CryptContext
from models.user import User, UserRole
from models.role import Role
from models.parish import Parish
from models.deanery import Deanery
from mailer.service import send_welcome_email, send_password_reset_email

import imghdr
import os
import logging
from datetime import date

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
logger = logging.getLogger(__name__)


@strawberry.type
class UserQuery:
    @strawberry.field
    def user(self, info: Info, id: int) -> Optional[UserType]:
        if not get_current_user(info):
            raise Exception("Unauthorized")
        db = SessionLocal()
        return get_user_by_id(db, id)

    @strawberry.field
    def users(self, info: Info, input: SearchInput) -> UserListResponse:
        current_user = get_current_user(info)
        if not user_has_permission(current_user, "users.view"):
            raise Exception("Unauthorized!")

        db = SessionLocal()
        query = db.query(User).order_by(User.id.desc(), User.parish_id.asc())

        if input.search.strip():
            search = f"%{input.search.strip()}%"
            query = query.filter(User.name.ilike(search))

        if input.parish_id is not None:
            query = query.filter(User.parish_id == input.parish_id)

        total_count = query.count()
        offset = (input.page - 1) * input.limit
        users = query.offset(offset).limit(input.limit).all()

        result = [
            UserType(
                id=u.id, name=u.name, email=u.email, phonenumber=u.phonenumber,
                dateofbirth=u.dateofbirth, idnumber=u.idnumber, baptismref=u.baptismref,
                profile_pic=u.profile_pic, role=RoleEnum(u.role.value), status=UserStatus(u.status.value),
                parish=u.parish, created_at=u.created_at, updated_at=u.updated_at
            )
            for u in users
        ]
        return UserListResponse(users=result, totalCount=total_count)


@strawberry.type
class UserMutation:
    # NOTE: the old ungated `create_user` mutation has been removed.
    # `register` is now the single, properly-gated entry point for creating users.

    @strawberry.mutation
    def register(self, info: Info, input: RegisterInput) -> UserType:
        db = SessionLocal()
        current_user = get_current_user(info)
        if not current_user:
            raise Exception("Unauthorized")
        if not user_has_permission(current_user, "users.create"):
            raise Exception("Unauthorized: You do not have permission to register members.")
        if not can_manage_parish(db, current_user, input.parish_id):
            raise Exception("Unauthorized: You can only register members within your own parish/deanery.")

        existing_user = get_user_by_email(db, input.email)
        if existing_user:
            raise Exception("User with this email already exists")

        user = create_user(
            db, input.name, input.email, input.phonenumber, input.dateofbirth,
            input.idnumber, input.baptismref, input.password, input.role.value,
            input.status.value, input.profile_pic, input.parish_id
        )

        # Assign the new user's role in the permission system (legacy `role`
        # column is set by create_user() already; this keeps model_has_roles in sync).
        role_obj = db.query(Role).filter(Role.name == input.role.value).first()
        if role_obj:
            user.roles.append(role_obj)

        if user.role == UserRole.parish_member and user.dateofbirth:
            today = date.today()
            age = today.year - user.dateofbirth.year - ((today.month, today.day) < (user.dateofbirth.month, user.dateofbirth.day))
            if age >= 27:
                user.status = UserStatus.archived_member.value

        info.context["background_tasks"].add_task(send_welcome_email, user.email, user.name)
        db.commit()
        db.refresh(user)

        return UserType(
            id=user.id, name=user.name, email=user.email, phonenumber=user.phonenumber,
            dateofbirth=user.dateofbirth, idnumber=user.idnumber, baptismref=user.baptismref,
            role=user.role, status=user.status, profile_pic=user.profile_pic, parish=user.parish,
            created_at=user.created_at, updated_at=user.updated_at
        )

    @strawberry.mutation
    def update_user(self, info: Info, input: UpdateUserInput) -> Optional[UserType]:
        current_user = get_current_user(info)
        if not current_user:
            raise Exception("Unauthorized")

        db = SessionLocal()
        try:
            target_user = db.query(User).filter(User.id == input.id).first()
            if not target_user:
                raise Exception("User not found")

            is_self = current_user.id == input.id
            if is_self:
                if not user_has_permission(current_user, "users.update.self"):
                    raise Exception("Unauthorized: You do not have permission to update your own profile.")
            else:
                if not user_has_permission(current_user, "users.update"):
                    raise Exception("Unauthorized: You do not have permission to update other members.")
                if not can_manage_parish(db, current_user, target_user.parish_id):
                    raise Exception("Unauthorized: You can only update members within your own parish/deanery.")

            if input.email:
                existing_email = db.query(User).filter(User.email == input.email, User.id != input.id).first()
                if existing_email:
                    raise Exception("Email is already in use by another user.")

            if input.phonenumber:
                existing_phone = db.query(User).filter(User.phonenumber == input.phonenumber, User.id != input.id).first()
                if existing_phone:
                    raise Exception("Phone number is already in use by another user.")

            updated_user = update_user(
                db, input.id, input.name, input.email, input.phonenumber, input.dateofbirth,
                input.idnumber, input.baptismref, input.password, input.role.value,
                input.status.value, input.parish_id
            )

            return UserType(
                id=updated_user.id, name=updated_user.name, email=updated_user.email,
                phonenumber=updated_user.phonenumber, dateofbirth=updated_user.dateofbirth,
                idnumber=updated_user.idnumber, baptismref=updated_user.baptismref,
                role=updated_user.role, status=updated_user.status, profile_pic=updated_user.profile_pic,
                parish=updated_user.parish, created_at=updated_user.created_at, updated_at=updated_user.updated_at
            )
        except Exception as e:
            db.rollback()
            raise Exception(f"Update failed: {str(e)}")
        finally:
            db.close()

    @strawberry.mutation
    def delete_user(self, info: Info, id: int) -> Optional[UserType]:
        current_user = get_current_user(info)
        if not current_user:
            raise Exception("Unauthorized")

        db = SessionLocal()
        try:
            target_user = db.query(User).filter(User.id == id).first()
            if not target_user:
                raise Exception("User not found")

            if not user_has_permission(current_user, "users.delete"):
                raise Exception("Unauthorized!")
            if not can_manage_parish(db, current_user, target_user.parish_id):
                raise Exception("Unauthorized: You can only delete members within your own parish/deanery.")

            return delete_user(db, id)
        finally:
            db.close()

    @strawberry.mutation
    def login(self, input: LoginInput) -> Optional[LoginPayload]:
        db = SessionLocal()
        try:
            identifier = input.username
            if not identifier:
                raise Exception("Please provide either email or phone number.")

            user = authenticate_user(db, identifier, input.password)
            if not user:
                raise Exception("Invalid credentials")

            user = (
                db.query(User)
                .options(
                    joinedload(User.parish).joinedload(Parish.deanery).joinedload(Deanery.zone),
                    joinedload(User.roles).joinedload(Role.permissions),
                )
                .filter(User.id == user.id)
                .first()
            )

            token = create_access_token(data={"sub": user.phonenumber or user.email})

            return LoginPayload(
                token=TokenType(access_token=token, token_type="bearer"),
                user=UserType(
                    id=user.id, name=user.name, email=user.email, phonenumber=user.phonenumber,
                    dateofbirth=user.dateofbirth, idnumber=user.idnumber, baptismref=user.baptismref,
                    role=user.role, status=user.status, parish=user.parish, profile_pic=user.profile_pic,
                    created_at=user.created_at, updated_at=user.updated_at,
                    permissions=get_user_permission_names(user),
                )
            )
        finally:
            db.close()

    @strawberry.mutation
    async def upload_profile_pic(self, user_id: int, file: Upload) -> UploadProfilePicResponse:
        db = SessionLocal()
        user = db.query(User).get(user_id)
        if not user:
            raise Exception("User not found.")

        allowed_types = ['jpeg', 'png', 'jpg']
        file_type = imghdr.what(file.file)
        if file_type not in allowed_types:
            raise Exception("Invalid file type. Only png, jpeg,jpg are allowed.")
        file.file.seek(0, 2)
        file_size = file.file.tell()
        if file_size > 500 * 1024:
            raise Exception("File too large. Maximum allowed size is 500KB.")

        file.file.seek(0)
        contents = await file.read()
        filename = f"user_{user_id}_profile.{file_type}"
        filepath = f"static/profile_pics/{filename}"
        with open(filepath, "wb") as f:
            f.write(contents)

        user.profile_pic = filename
        db.commit()
        db.refresh(user)

        return UploadProfilePicResponse(
            message="Profile picture updated successfully!",
            user=UserType(
                id=user.id, name=user.name, email=user.email, phonenumber=user.phonenumber,
                dateofbirth=user.dateofbirth, idnumber=user.idnumber, baptismref=user.baptismref,
                role=user.role, parish=user.parish, status=user.status, profile_pic=user.profile_pic,
                created_at=user.created_at, updated_at=user.updated_at
            )
        )

    @strawberry.mutation
    def reset_password(self, info: Info, input: ResetPasswordInput) -> UpdateUserPasswordResponse:
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

        return UpdateUserPasswordResponse(
            message="Password reset successful",
            user=UserType(
                id=user.id, name=user.name, email=user.email, phonenumber=user.phonenumber,
                dateofbirth=user.dateofbirth, idnumber=user.idnumber, baptismref=user.baptismref,
                role=user.role, parish=user.parish, status=user.status, profile_pic=user.profile_pic,
                created_at=user.created_at, updated_at=user.updated_at
            )
        )

    @strawberry.mutation
    def update_user_role(self, info: Info, input: UpdateUserRoleInput) -> UserType:
        db = SessionLocal()
        try:
            current_user = get_current_user(info)
            if not current_user:
                raise Exception("Authentication required. Please log in.")

            target_user = db.query(User).filter(User.id == input.user_id).first()
            if not target_user:
                raise Exception(f"User with ID {input.user_id} not found.")

            if not user_has_permission(current_user, "users.role.assign"):
                raise Exception("Unauthorized: You do not have permission to change user roles.")

            if current_user.id == target_user.id:
                raise Exception("Action forbidden: You cannot change your own role.")

            protected_role_names = {"super_user", "ysc_chaplain"}
            existing_role_names = {r.name for r in target_user.roles}
            if existing_role_names & protected_role_names:
                raise Exception("Action forbidden: This user's role cannot be changed.")

            new_role = db.query(Role).filter(Role.name == input.new_role.value).first()
            if not new_role:
                raise Exception(f"Role '{input.new_role.value}' does not exist.")

            target_user.roles = [new_role]       # new permission system, source of truth
            target_user.role = input.new_role.value  # legacy column, kept in sync during transition

            db.commit()
            db.refresh(target_user)
            return target_user
        finally:
            db.close()

    @strawberry.mutation
    def request_password_reset(self, info: Info, identifier: str) -> str:
        """
        Self-service password reset. Unauthenticated by design — a member who
        forgot their password can't present a Bearer token. Always returns a
        generic message regardless of whether the identifier matched a user,
        to avoid leaking which emails/phone numbers exist in the system.
        """
        db = SessionLocal()
        try:
            target_user = get_user_by_identifier(db, identifier)
            if target_user:
                try:
                    new_password = generate_default_password(target_user)
                    target_user.password = pwd_context.hash(new_password)
                    db.commit()
                    db.refresh(target_user)
                    info.context["background_tasks"].add_task(
                        send_password_reset_email, target_user.email, target_user.name, new_password
                    )
                except Exception:
                    # Catches missing-DOB (ValueError) as well as any DB/email failure.
                    # Never let this surface differently than the "no match" case below —
                    # doing so would let an attacker distinguish valid identifiers by error shape.
                    db.rollback()
                    logger.exception("Password reset failed for identifier %s", identifier)

            return "If an account matches these details, a password reset email has been sent."
        finally:
            db.close()

    @strawberry.mutation
    def reset_member_password(self, info: Info, user_id: int) -> UpdateUserPasswordResponse:
        current_user = get_current_user(info)
        if not current_user:
            raise Exception("Unauthorized")

        db = SessionLocal()
        try:
            target_user = db.query(User).filter(User.id == user_id).first()
            if not target_user:
                raise Exception("User not found")

            if not user_has_permission(current_user, "users.password.reset"):
                raise Exception("Unauthorized: You do not have permission to reset member passwords.")
            if not can_manage_parish(db, current_user, target_user.parish_id):
                raise Exception("Unauthorized: You can only reset passwords for members within your own parish/deanery.")

            new_password = generate_default_password(target_user)
            target_user.password = pwd_context.hash(new_password)
            db.commit()
            db.refresh(target_user)

            info.context["background_tasks"].add_task(
                send_password_reset_email, target_user.email, target_user.name, new_password
            )

            return UpdateUserPasswordResponse(
                message="Password reset to default successfully",
                user=UserType(
                    id=target_user.id, name=target_user.name, email=target_user.email,
                    phonenumber=target_user.phonenumber, dateofbirth=target_user.dateofbirth,
                    idnumber=target_user.idnumber, baptismref=target_user.baptismref,
                    role=target_user.role, parish=target_user.parish, status=target_user.status,
                    profile_pic=target_user.profile_pic, created_at=target_user.created_at,
                    updated_at=target_user.updated_at
                )
            )
        finally:
            db.close()


schema = strawberry.Schema(query=UserQuery, mutation=UserMutation)