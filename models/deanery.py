from sqlalchemy import Column, Integer, String, ForeignKey, event
from config.db import Base
from sqlalchemy.orm import relationship

class Deanery(Base):
    __tablename__ = "deaneries"
    id = Column(Integer, primary_key = True, index=True)
    name = Column(String(100), unique = True, index = True)
    prefix = Column(String(6), unique=True, nullable=True)  
    zone_id = Column(Integer, ForeignKey("zones.id"))
    zone = relationship("Zone", back_populates="deaneries")

    parishes = relationship("Parish", back_populates="deanery")


@event.listens_for(Deanery, "before_insert")
@event.listens_for(Deanery, "before_update")
def generate_prefix(mapper, connection, target):

    if not target.zone_id:
        return  # Skip if no zone assigned yet

    # Get the zone name safely from relationship or direct join
    zone = target.zone
    if not zone:
        return

    zone_letter = zone.name.strip().split()[-1][-1].upper()  # "ZONE A" → "A"
    deanery_initials = target.name.strip().replace("DEANERY", "").strip().upper()[:3]

    new_prefix = f"{zone_letter}-{deanery_initials}"

    # Only update if it changed or is empty
    if target.prefix != new_prefix:
        target.prefix = new_prefix
    