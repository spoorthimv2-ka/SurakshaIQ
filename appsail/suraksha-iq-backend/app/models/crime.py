import uuid
from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
import enum
from app.database.postgres.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.district import District
    from app.models.police_station import PoliceStation

class CrimeStatus(str, enum.Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    CLOSED = "CLOSED"
    COLD = "COLD"

class Crime(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "crimes"

    fir_number: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    crime_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Event time
    incident_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    
    # Status
    status: Mapped[CrimeStatus] = mapped_column(SQLEnum(CrimeStatus, name="crime_status_enum"), default=CrimeStatus.OPEN, index=True, nullable=False)

    # Geospatial Location
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Foreign Keys
    district_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("districts.id"), index=True, nullable=False)
    police_station_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("police_stations.id"), index=True, nullable=False)

    # Relationships
    district: Mapped["District"] = relationship("District", back_populates="crimes")
    police_station: Mapped["PoliceStation"] = relationship("PoliceStation", back_populates="crimes")
