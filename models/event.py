# models/event.py
import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Time, Enum, Numeric
from sqlalchemy.orm import relationship
from config.db import Base


class EventScope(str, enum.Enum):
    adn = "adn"
    zone = "zone"
    deanery = "deanery"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=False)
    charges = Column(Numeric(10, 2), nullable=False, default=0)
    days = Column(Integer, nullable=False)
    event_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    scope = Column(Enum(EventScope), nullable=False, default=EventScope.adn)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)
    deanery_id = Column(Integer, ForeignKey("deaneries.id"), nullable=True)

    creator = relationship("User", back_populates="events")
    zone = relationship("Zone", back_populates="events")
    deanery = relationship("Deanery", back_populates="events")