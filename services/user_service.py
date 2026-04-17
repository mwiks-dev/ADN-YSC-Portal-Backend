from models.user import User, UserStatus, UserRole
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
import os
from datetime import datetime, timedelta, date

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db:Session, user_email:str):
    return db.query(User).filter(User.email == user_email).first()

def get_user_by_identifier(db:Session, identifier:str):
    if "@" in identifier:
        return db.query(User).filter(User.email == identifier).first()
    # Otherwise, assume it’s a phone number
    return db.query(User).filter(User.phonenumber == identifier).first()

def get_users(db: Session):
    return db.query(User).all()

def create_user(db: Session, name: str, email: str, phonenumber: str, dateofbirth:date ,idnumber:int,baptismref:str, password: str, role:str,status:str, profile_pic:str, parish_id:int):
    hashed_password = pwd_context.hash(password)
    user = User(name=name, email=email, phonenumber=phonenumber,dateofbirth=dateofbirth, idnumber=idnumber,baptismref=baptismref, password=hashed_password, role=role, status=status, profile_pic=profile_pic, parish_id=parish_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, id: int, name: str, email: str, phonenumber: str,dateofbirth:date ,idnumber:int,baptismref:str, password: str,role:str, status:str, parish_id:int):
    user = db.query(User).filter(User.id == id).first()
    if user:
        user.name = name
        user.email = email
        user.phonenumber = phonenumber
        user.dateofbirth = dateofbirth
        user.idnumber = idnumber
        user.baptismref = baptismref
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
    to_encode.update({"exp": expire,  "sub": data.get("sub")})
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
