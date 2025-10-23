from sqlalchemy import Column, Integer, String, ForeignKey, event
from sqlalchemy.orm import relationship
from config.db import Base
from scripts.generate_parish_prefixes import generate_parish_prefixes
class Parish(Base):
    __tablename__ = "parishes"
    id = Column(Integer, primary_key = True, index=True)
    name = Column(String(100), index = True)
    prefix = Column(String(10), nullable=True)
    deanery_id = Column(Integer, ForeignKey("deaneries.id"))
    
    deanery = relationship("Deanery", back_populates="parishes", lazy="joined")
    users = relationship("User", back_populates="parish")
    outstations = relationship("Outstation", back_populates="parish", cascade="all, delete", passive_deletes = True)

@event.listens_for(Parish, "before_insert")
@event.listens_for(Parish, "before_update")
def set_parish_prefix(mapper, connection, target):
    if not target.prefix or target.name:
        target.prefix = generate_parish_prefixes(target.name)