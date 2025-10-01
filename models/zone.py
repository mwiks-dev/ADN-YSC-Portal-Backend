from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config.db import Base

class Zone(Base):
    __tablename__ = "zones"
    id = Column(Integer, primary_key = True, index=True)
    name = Column(String(100), unique = True, index = True)
    
    deaneries = relationship("Deanery", back_populates="zone")