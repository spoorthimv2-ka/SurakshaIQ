from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
from app.database.postgres.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.police_station import PoliceStation
    from app.models.crime import Crime

class District(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "districts"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    region_code: Mapped[str] = mapped_column(String(50), nullable=True)

    # Geospatial boundaries or center
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    police_stations: Mapped[List["PoliceStation"]] = relationship("PoliceStation", back_populates="district")
    crimes: Mapped[List["Crime"]] = relationship("Crime", back_populates="district")
