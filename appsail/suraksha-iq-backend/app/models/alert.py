from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database.postgres.base import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String, nullable=False) # e.g., ANOMALY, HOTSPOT, REPEAT_OFFENDER, SYSTEM
    severity = Column(String, nullable=False) # e.g., HIGH, MEDIUM, LOW
    status = Column(String, nullable=False, default="active") # active, acknowledged, resolved
    message = Column(String, nullable=False)
    district_id = Column(String, ForeignKey("districts.id"), nullable=True) # Null if state-wide
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    district = relationship("District", backref="district_alerts")
