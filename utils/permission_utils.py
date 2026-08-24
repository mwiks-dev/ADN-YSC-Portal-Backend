from typing import Iterable

def user_has_role(user, role_name: str) -> bool:
    return bool(user) and any(r.name == role_name for r in user.roles)

def user_has_permission(user, permission_name: str) -> bool:
    if not user:
        return False
    for role in user.roles:
        names = {p.name for p in role.permissions}
        if permission_name in names or "*" in names:
            return True
    return False

def user_has_any_permission(user, permission_names: Iterable[str]) -> bool:
    return any(user_has_permission(user, p) for p in permission_names)

def get_user_permission_names(user) -> list[str]:
    if not user:
        return []
    names = set()
    for role in user.roles:
        for perm in role.permissions:
            names.add(perm.name)
    return sorted(names)