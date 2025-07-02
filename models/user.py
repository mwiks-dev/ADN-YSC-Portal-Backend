from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    phonenumber = Column(String(20))
    password = Column(String(255))
    
    parish_id = Column(Integer, ForeignKey("parishes.id"))
    parish = relationship("Parish", backref="users")
