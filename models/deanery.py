from sqlalchemy import Column, Integer, String, ForeignKey
from config.db import Base
from sqlalchemy.orm import relationship

class Deanery(Base):
    __tablename__ = "deaneries"
    id = Column(Integer, primary_key = True, index=True)
    name = Column(String(100), unique = True, index = True)
    zone_id = Column(Integer, ForeignKey("zones.id"))

    zone = relationship("Zone", back_populates="deaneries")


    parishes = relationship("Parish", back_populates="deanery")
    