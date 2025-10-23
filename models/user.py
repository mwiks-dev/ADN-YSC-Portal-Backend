from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Date, event
from sqlalchemy.orm import relationship, Session
from config.db import Base
from utils.membership_utils import generate_membership_no
import enum

class UserRole(str,enum.Enum):
    parish_member = "parish_member"
    parish_moderator = "parish_moderator"
    deanery_moderator = "deanery_moderator"
    ysc_coordinator = "ysc_coordinator"
    ysc_chaplain = "ysc_chaplain"
    super_user = "super_user"

class UserStatus(str, enum.Enum):
    active_member = "Active"
    archived_member = "Archived"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    phonenumber = Column(String(20),unique=True, index=True)
    dateofbirth = Column(Date)
    idnumber = Column(Integer, unique = True)
    baptismref = Column(String(30))
    password = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.parish_member)
    status = Column(Enum(UserStatus))
    profile_pic = Column(String(255), nullable=True)

    membership_no = Column(String(20), index=True, unique=True, nullable=True)
    parish_id = Column(Integer, ForeignKey("parishes.id"))
    parish = relationship("Parish", back_populates="users")
    created_at = Column(Date)
    updated_at = Column(Date)

@event.listens_for(User, "before_insert")
def set_membership_no(mapper, connection, target):
    """Automatically assign a membership number before inserting a user."""
    db = Session(bind=connection)
    try:
        if not target.membership_no and target.parish_id:
            target.membership_no = generate_membership_no(db, target.parish_id)
    finally:
        db.close()