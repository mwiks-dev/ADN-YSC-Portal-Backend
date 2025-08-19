import factory
from faker import Faker
import random
from datetime import date
from models.user import User, UserRole
from config.db import SessionLocal  # your DB session

fake = Faker()

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = SessionLocal()
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker("name")
    email = factory.LazyAttribute(lambda _: fake.unique.email())
    phonenumber = factory.LazyAttribute(lambda _: "07" + "".join(str(random.randint(0, 9)) for _ in range(8)))
    dateofbirth = factory.LazyFunction(lambda: fake.date_of_birth(minimum_age=16, maximum_age=26))
    idnumber = factory.LazyAttribute(lambda _: random.randint(10000000, 99999999))
    baptismref = factory.LazyAttribute(lambda _: fake.bothify(text="BAP###??"))
    password = factory.LazyAttribute(lambda _: fake.password(length=12))
    role = factory.LazyFunction(lambda: random.choice(list(UserRole)))
    
    # Option 1: leave parish_id null
    parish_id = factory.LazyAttribute(lambda _: random.randint(1, 125))
    
    # Option 2 (if ParishFactory exists):
    # parish = factory.SubFactory("app.factories.parish_factory.ParishFactory")
