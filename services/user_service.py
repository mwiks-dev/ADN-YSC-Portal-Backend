from models.user import User
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
import os
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db:Session, user_email:str):
    return db.query(User).filter(User.email == user_email).first()

def get_users(db: Session):
    return db.query(User).all()

def create_user(db: Session, name: str, email: str, phonenumber: str, password: str, role:str = "parish_member", parish_id:int = 57):
    hashed_password = pwd_context.hash(password)
    user = User(name=name, email=email, phonenumber=phonenumber, password=hashed_password, role=role, parish_id=parish_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, id: int, name: str, email: str, phonenumber: str, password: str,role:str, parish_id:int):
    user = db.query(User).filter(User.id == id).first()
    if user:
        user.name = name
        user.email = email
        user.phonenumber = phonenumber
        user.password = pwd_context.hash(password)
        user.role = role
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

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not pwd_context.verify(password, user.password):
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
        email: str = payload.get("sub")
        if email is None:
            raise JWTError("Missing subject")
        return email
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
