from strawberry.types import Info
from typing import Optional
from services.user_service import verify_token, get_user_by_email
from config.db import SessionLocal
from schemas.graphql.shared_types import UserType


def is_chaplain(user) -> bool:
    return user and getattr(user, "role", None) == "ysc_chaplain"

def is_ysc_coordinator(user) -> bool:
    return user and getattr(user, "role", None) == "ysc_coordinator"

def is_deanery_moderator(user) -> bool:
    return user and getattr(user, "role", None) == "deanery_moderator"

def is_parish_moderator(user) -> bool:
    return user and getattr(user, "role", None) == "parish_moderator"

def is_parish_member(user) -> bool:
    return user and getattr(user, "role", None) == "parish_member"

def is_authenticated(user) -> bool:
    return user is not None

def can_register_users(user) -> bool:
    return any([
        is_chaplain(user),
        is_ysc_coordinator(user),
        is_deanery_moderator(user),
        is_parish_moderator(user)
    ])

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