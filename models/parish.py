from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config.db import Base

class Parish(Base):
    __tablename__ = "parishes"
    id = Column(Integer, primary_key = True, index=True)
    name = Column(String(100), index = True)
    deanery_id = Column(Integer, ForeignKey("deaneries.id"))
    
    deanery = relationship("Deanery", back_populates="parishes", lazy="joined")
    users = relationship("User", back_populates="parish")
    outstations = relationship("Outstation", back_populates="parish", cascade="all, delete", passive_deletes = True)
