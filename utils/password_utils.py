import secrets
import string

def generate_default_password(user) -> str:
    if not user.dateofbirth:
        raise ValueError("Cannot generate default password: user has no date of birth on file.")
    return str(user.dateofbirth.year)