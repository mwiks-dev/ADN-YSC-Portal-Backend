from sqlalchemy import Column, Integer, String
from config.db import Base
from sqlalchemy.orm import relationship

class Deanery(Base):
    __tablename__ = "deaneries"
    id = Column(Integer, primary_key = True, index=True)
    name = Column(String(100), unique = True, index = True)

    parishes = relationship("Parish", back_populates="deanery", foreign_keys="Parish.deanery_id")
    