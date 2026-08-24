# utils/auth_utils.py
from strawberry.types import Info
from typing import Optional
from services.user_service import verify_token, get_user_by_identifier
from config.db import SessionLocal
from models.user import User
from utils.permission_utils import user_has_role, user_has_permission


def get_current_user(info: Info) -> Optional[User]:
    auth_header = info.context.get("request").headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    username = verify_token(token)
    if not username:
        raise Exception("Unauthorized")

    db = SessionLocal()
    try:
        return get_user_by_identifier(db, username)
    finally:
        db.close()


# --- Deprecated bridge functions ---
# Kept for backward compatibility with zone_schema.py, parish_schema.py,
# deanery_schema.py, event_parish_registration_service.py.
# New code should call user_has_permission()/user_has_role() directly.
# TODO: migrate these call sites, then delete everything below.

def is_chaplain(user) -> bool:
    return user_has_role(user, "ysc_chaplain")

def is_ysc_coordinator(user) -> bool:
    return user_has_role(user, "ysc_coordinator")

def is_deanery_moderator(user) -> bool:
    return user_has_role(user, "deanery_moderator")

def is_parish_moderator(user) -> bool:
    return user_has_role(user, "parish_moderator")

def is_parish_member(user) -> bool:
    return user_has_role(user, "parish_member")

def is_superuser(user) -> bool:
    return user_has_role(user, "super_user")

def is_authenticated(user) -> bool:
    return user is not None

def can_register_users(user) -> bool:
    return user_has_permission(user, "users.create")