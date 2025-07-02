from sqlalchemy import Column, Integer, String, ForeignKey
from config.db import Base
from sqlalchemy.orm import relationship

class Outstation(Base):
    __tablename__ = "outstations"
    id = Column(Integer, primary_key = True, index=True)
    name = Column(String(100), index = True)
    parish_id = Column(Integer, ForeignKey("parishes.id"))

    parish = relationship("Parish", back_populates="outstations")