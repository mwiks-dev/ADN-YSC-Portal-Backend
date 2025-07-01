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
