from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from config.db import Base
import enum

class UserRole(str,enum.Enum):
    parish_member = "parish_member"
    parish_moderator = "parish_moderator"
    deanery_moderator = "deanery_moderator"
    ysc_coordinator = "ysc_coordinator"
    ysc_chaplain = "ysc_chaplain"
    super_user = "super_user"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    phonenumber = Column(String(20))
    password = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.parish_member)
    
    parish_id = Column(Integer, ForeignKey("parishes.id"))
    parish = relationship("Parish", back_populates="users")
