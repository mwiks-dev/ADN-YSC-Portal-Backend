from sqlalchemy.orm import Session
from models.parish import Parish
from utils.permission_utils import user_has_role

# Roles with no scoping restriction — can manage members anywhere
FULL_ACCESS_ROLES = {"super_user", "ysc_chaplain", "ysc_coordinator"}

def user_has_full_access(user) -> bool:
    return any(user_has_role(user, r) for r in FULL_ACCESS_ROLES)

def get_deanery_id_for_parish(db: Session, parish_id: int) -> int | None:
    parish = db.query(Parish).filter(Parish.id == parish_id).first()
    return parish.deanery_id if parish else None

def can_manage_parish(db: Session, current_user, target_parish_id: int) -> bool:
    """
    Determines whether current_user is allowed to create/manage a member
    belonging to target_parish_id, based on the Zone > Deanery > Parish hierarchy.
    """
    if user_has_full_access(current_user):
        return True

    if user_has_role(current_user, "parish_moderator"):
        return current_user.parish_id == target_parish_id

    if user_has_role(current_user, "deanery_moderator"):
        current_deanery_id = get_deanery_id_for_parish(db, current_user.parish_id)
        target_deanery_id = get_deanery_id_for_parish(db, target_parish_id)
        return current_deanery_id is not None and current_deanery_id == target_deanery_id

    return False