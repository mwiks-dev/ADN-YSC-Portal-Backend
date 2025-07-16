# Explicitly import all models to register relationships
import models.deanery
import models.parish
import models.user
import models.outstation

import os
from dotenv import load_dotenv
from models.user import User, UserRole
from config.db import SessionLocal
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
load_dotenv()


def seed_super_user():
    db = SessionLocal()
    email = os.getenv("SUPERUSER_EMAIL")
    existing = db.query(User).filter(User.email == email).first()

    if existing:
        print("Super user already exists.")
        return

    hashed_pw = pwd_context.hash(os.getenv("SUPERUSER_PWD"))
    super_user = User(
        name= os.getenv("SUPERUSER_NAME"),
        email=email,
        phonenumber= os.getenv("SUPERUSER_PHNO"),
        password=hashed_pw,
        role=UserRole.super_user,  
        parish_id=107  
    )

    db.add(super_user)
    db.commit()
    print("Super user created.")

if __name__ == "__main__":
    seed_super_user()
