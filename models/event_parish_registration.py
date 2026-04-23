from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, UniqueConstraint, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from config.db import Base


class EventParishRegistration(Base):
    __tablename__ = "event_parish_registrations"

    id = Column(Integer, primary_key=True, index=True)

    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    parish_id = Column(Integer, ForeignKey("parishes.id"), nullable=False)

    arrival_time = Column(DateTime, nullable=True)               
    number_of_participants = Column(Integer, nullable=False, default=0)
    is_cleared = Column(Boolean, nullable=False, default=True)
    clearance_note = Column(Text, nullable=True)
    fine_amount = Column(Float, nullable=False, default=0.0)

    registered_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    cleared_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    admitted_by = Column(Integer, ForeignKey("users.id"), nullable=True)           

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("event_id", "parish_id", name="uq_event_parish_registration"),
    )

    event = relationship("Event", back_populates="parish_registrations")
    parish = relationship("Parish", back_populates="event_registrations")

    registrar = relationship("User", foreign_keys=[registered_by])
    clearer = relationship("User", foreign_keys=[cleared_by])
    admitter = relationship("User", foreign_keys=[admitted_by])

    @property
    def attendance_status(self) -> str:
        # Not yet admitted at all
        if self.arrival_time is None:
            return "registered"

        # Admitted but pending clearance (late + fine outstanding)
        if self.arrival_time and not self.is_cleared:
            return "pending_clearance"

        # Admitted and cleared (on time or fine waived)
        if self.arrival_time and self.is_cleared:
            return "attended"

        return "absent"