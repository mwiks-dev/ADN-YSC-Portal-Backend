from models.user import User
from sqlalchemy.orm import Session

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session):
    return db.query(User).all()

def create_user(db: Session, name: str, email: str, phonenumber: str, password: str):
    user = User(name=name, email=email, phonenumber=phonenumber, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, id: int, name: str, email: str, phonenumber: str, password: str):
    user = db.query(User).filter(User.id == id).first()
    if user:
        user.name = name
        user.email = email
        user.phonenumber = phonenumber
        user.password = password
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user
