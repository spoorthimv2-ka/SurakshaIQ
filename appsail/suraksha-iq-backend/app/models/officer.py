import uuid
from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.enums import Role, JurisdictionType, AccountStatus
from typing import TYPE_CHECKING, Optional
from app.database.postgres.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.police_station import PoliceStation

class Officer(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "officers"

    catalyst_user_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    role: Mapped[Role] = mapped_column(SQLEnum(Role, native_enum=False, length=50), nullable=False)
    rank: Mapped[str | None] = mapped_column(String(100), nullable=True)
    designation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    badge_number: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)

    # Jurisdiction
    jurisdiction_type: Mapped[JurisdictionType] = mapped_column(
        SQLEnum(JurisdictionType, native_enum=False, length=20),
        nullable=False,
        default=JurisdictionType.STATION,
    )
    police_station_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("police_stations.id"), index=True, nullable=True)
    district_id: Mapped[uuid.UUID | None] = mapped_column(String(50), index=True, nullable=True)

    # Account security
    account_status: Mapped[AccountStatus] = mapped_column(
        SQLEnum(AccountStatus, native_enum=False, length=20),
        nullable=False,
        default=AccountStatus.ACTIVE,
    )
    last_login: Mapped[str | None] = mapped_column(String(50), nullable=True)
    failed_attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    locked_until: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    police_station: Mapped["PoliceStation"] = relationship("PoliceStation", back_populates="officers")
