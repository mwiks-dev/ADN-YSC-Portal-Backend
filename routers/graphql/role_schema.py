import strawberry
from strawberry.types import Info
from typing import List
from config.db import SessionLocal
from models.role import Role
from models.permission import Permission
from routers.graphql.role_type import RoleType, PermissionType, AssignPermissionInput
from utils.auth_utils import get_current_user
from utils.permission_utils import user_has_permission
from sqlalchemy.orm import joinedload


def _require_manage_permissions(info: Info):
    user = get_current_user(info)
    if not user:
        raise Exception("Unauthorized")
    # only wildcard-holders (super_user, ysc_chaplain, ysc_coordinator) manage RBAC itself
    if not user_has_permission(user, "*"):
        raise Exception("Unauthorized: You do not have permission to manage roles/permissions.")
    return user


@strawberry.type
class RoleQuery:
    @strawberry.field
    def roles(self, info: Info) -> List[RoleType]:
        _require_manage_permissions(info)
        db = SessionLocal()
        try:
            return db.query(Role).options(joinedload(Role.permissions)).all()
        finally:
            db.close()

    @strawberry.field
    def permissions(self, info: Info) -> List[PermissionType]:
        _require_manage_permissions(info)
        db = SessionLocal()
        try:
            return db.query(Permission).all()
        finally:
            db.close()


@strawberry.type
class RoleMutation:
    @strawberry.mutation

    def assign_permission_to_role(self, info: Info, input: AssignPermissionInput) -> RoleType:
        _require_manage_permissions(info)
        db = SessionLocal()
        try:
            role = db.query(Role).options(joinedload(Role.permissions)).filter(Role.id == input.role_id).first()
            if not role:
                raise Exception("Role not found")
            perm = db.query(Permission).filter(Permission.id == input.permission_id).first()
            if not perm:
                raise Exception("Permission not found")
            if perm not in role.permissions:
                role.permissions.append(perm)
                db.commit()
                db.refresh(role)
            return role
        finally:
            db.close()

    @strawberry.mutation
    def remove_permission_from_role(self, info: Info, input: AssignPermissionInput) -> RoleType:
        _require_manage_permissions(info)
        db = SessionLocal()
        try:
            role = db.query(Role).options(joinedload(Role.permissions)).filter(Role.id == input.role_id).first()
            if not role:
                raise Exception("Role not found")
            perm = db.query(Permission).filter(Permission.id == input.permission_id).first()
            if not perm:
                raise Exception("Permission not found")
            if perm in role.permissions:
                role.permissions.remove(perm)
                db.commit()
                db.refresh(role)
            return role
        finally:
            db.close()