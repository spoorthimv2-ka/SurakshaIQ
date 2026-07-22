import uuid
from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.enums import Role
from typing import TYPE_CHECKING
from app.database.postgres.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.police_station import PoliceStation

class Officer(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "officers"

    catalyst_user_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    role: Mapped[Role] = mapped_column(SQLEnum(Role, native_enum=False, length=50), nullable=False)
    rank: Mapped[str | None] = mapped_column(String(100), nullable=True)
    designation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Foreign Keys (nullable because Admins or State-level officers might not belong to a specific station)
    police_station_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("police_stations.id"), index=True, nullable=True)

    # Relationships
    police_station: Mapped["PoliceStation"] = relationship("PoliceStation", back_populates="officers")
