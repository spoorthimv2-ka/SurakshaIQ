from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
import uuid
from datetime import datetime, timezone
from app.database.postgres.base import Base
from sqlalchemy.orm import relationship

class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    report_type = Column(String, nullable=False) # e.g. DISTRICT_SUMMARY, INCIDENT_REPORT
    parameters_json = Column(JSONB, nullable=True) # stores filter criteria, like district_id, date ranges
    created_by_officer_id = Column(String, ForeignKey("officers.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    officer = relationship("Officer", backref="generated_reports")
