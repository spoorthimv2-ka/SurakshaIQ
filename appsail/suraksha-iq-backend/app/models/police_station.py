import uuid
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
from app.database.postgres.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.district import District
    from app.models.officer import Officer
    from app.models.crime import Crime

class PoliceStation(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "police_stations"

    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    station_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Location
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Foreign Keys
    district_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("districts.id"), index=True, nullable=False)

    # Relationships
    district: Mapped["District"] = relationship("District", back_populates="police_stations")
    officers: Mapped[List["Officer"]] = relationship("Officer", back_populates="police_station")
    crimes: Mapped[List["Crime"]] = relationship("Crime", back_populates="police_station")
