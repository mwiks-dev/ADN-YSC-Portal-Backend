from models.user import User
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from models.role import Role
from passlib.context import CryptContext
from jose import jwt, JWTError
import os
from datetime import datetime, timedelta, date
from typing import Optional
from utils.membership_utils import generate_membership_no


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MAX_MEMBERSHIP_RETRIES = 5

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def get_user_by_id(db: Session, user_id: int):
    return (
        db.query(User)
        .options(joinedload(User.roles).joinedload(Role.permissions))
        .filter(User.id == user_id)
        .first()
    )

def get_user_by_email(db: Session, user_email: str):
    return (
        db.query(User)
        .options(joinedload(User.roles).joinedload(Role.permissions))
        .filter(User.email == user_email)
        .first()
    )

def get_user_by_identifier(db: Session, identifier: str):
    query = db.query(User).options(joinedload(User.roles).joinedload(Role.permissions))
    if "@" in identifier:
        return query.filter(User.email == identifier).first()
    return query.filter(User.phonenumber == identifier).first()

def get_users(db: Session):
    return db.query(User).all()

def create_user(
    db: Session,
    name: str,
    email: str,
    phonenumber: str,
    dateofbirth: date,
    idnumber: int,
    baptismref: str,
    password: str,
    role: str,
    status: str,
    profile_pic: str,
    parish_id: int
):
    print("🔥 NEW CREATE_USER CODE IS RUNNING 🔥")
    hashed_password = pwd_context.hash(password)

    user = User(
        name=name,
        email=email,
        phonenumber=phonenumber,
        dateofbirth=dateofbirth,
        idnumber=idnumber,
        baptismref=baptismref,
        password=hashed_password,
        role=role,
        status=status,
        profile_pic=profile_pic,
        parish_id=parish_id,
        created_at=date.today(),
        updated_at=date.today(),
    )

    # ---------------------------------------------------------
    # Try to create the user
    # ---------------------------------------------------------
    for attempt in range(MAX_MEMBERSHIP_RETRIES):

        try:
            # Generate the membership number explicitly
            user.membership_no = generate_membership_no(
                db,
                parish_id
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            return user

        except IntegrityError as e:
            db.rollback()

            error_message = str(e.orig).lower()

            # -------------------------------------------------
            # Membership number collision
            # -------------------------------------------------
            if "membership_no" in error_message:

                print(
                    f"Membership number collision "
                    f"(attempt {attempt + 1}/{MAX_MEMBERSHIP_RETRIES})"
                )

                print(
                    f"Generated membership number: "
                    f"{user.membership_no}"
                )

                # Clear the number.
                # The next loop will generate a new one.
                user.membership_no = None

                continue

            # -------------------------------------------------
            # Email already exists
            # -------------------------------------------------
            elif "email" in error_message:

                raise ValueError(
                    f"A user with email '{email}' already exists."
                )

            # -------------------------------------------------
            # Phone number already exists
            # -------------------------------------------------
            elif "phonenumber" in error_message:

                raise ValueError(
                    f"A user with phone number "
                    f"'{phonenumber}' already exists."
                )

            # -------------------------------------------------
            # ID number already exists
            # -------------------------------------------------
            elif "idnumber" in error_message:

                raise ValueError(
                    f"A user with ID number "
                    f"'{idnumber}' already exists."
                )

            # -------------------------------------------------
            # Unknown database error
            # -------------------------------------------------
            else:
                raise

    # ---------------------------------------------------------
    # All membership-number attempts failed
    # ---------------------------------------------------------
    raise ValueError(
        "Failed to generate a unique membership number "
        f"after {MAX_MEMBERSHIP_RETRIES} attempts."
    )

def update_user(db: Session, id: int, name: str, email: str, phonenumber: str, dateofbirth: date, idnumber: int, baptismref: str, password: Optional[str], role: str, status: str, parish_id: int):
    user = db.query(User).filter(User.id == id).first()
    if user:
        user.name = name
        user.email = email
        user.phonenumber = phonenumber
        user.dateofbirth = dateofbirth
        user.idnumber = idnumber
        user.baptismref = baptismref
        if password:
            user.password = pwd_context.hash(password)
        user.role = role
        user.status = status
        user.parish_id = parish_id
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user

def authenticate_user(db: Session, identifier: str, password: str):
    # Try to find user by email first, else by phone
    user = (
        db.query(User)
        .filter((User.email == identifier) | (User.phonenumber == identifier))
        .first()
    )
    if not user or not pwd_context.verify(password, user.password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "sub": data.get("sub")})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise JWTError("Missing subject")
        return username
    except JWTError:
        return None

def reset_password(db: Session, email: str, old_password: str, new_password: str):
    user = get_user_by_email(db, email)
    if not user:
        raise Exception("User not found")
    if not pwd_context.verify(old_password, user.password):
        raise Exception("Old password is incorrect")

    user.password = pwd_context.hash(new_password)
    db.commit()
    db.refresh(user)
    return user