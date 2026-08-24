from config.db import SessionLocal
from models.role import Role
from models.permission import Permission

PERMISSIONS = [
    ("*", "Full access - bypasses all other permission checks"),
    ("users.view", "View user list / search"),
    ("users.create", "Create a new user"),
    ("users.update", "Update any user's profile"),
    ("users.update.self", "Update own profile"),
    ("users.delete", "Delete a user"),
    ("users.role.assign", "Change a user's role"),
]

# role_name -> list of permission names
ROLE_PERMISSIONS = {
    "super_user": ["*"],
    "ysc_chaplain": ["*"],
    "ysc_coordinator": ["*"],
    "deanery_moderator": ["users.view", "users.create", "users.update.self"],
    "parish_moderator": ["users.view", "users.create", "users.update.self"],
    "parish_member": ["users.update.self"],
}

def seed_roles_permissions():
    db = SessionLocal()
    try:
        perm_map = {}
        for name, description in PERMISSIONS:
            perm = db.query(Permission).filter_by(name=name).first()
            if not perm:
                perm = Permission(name=name, description=description)
                db.add(perm)
                db.flush()
            perm_map[name] = perm

        for role_name, perm_names in ROLE_PERMISSIONS.items():
            role = db.query(Role).filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name)
                db.add(role)
                db.flush()
            role.permissions = [perm_map[p] for p in perm_names]

        db.commit()
        print("Roles and permissions seeded.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_roles_permissions()