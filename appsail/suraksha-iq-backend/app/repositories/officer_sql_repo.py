from typing import Optional, Dict, Any
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.officer import Officer

class OfficerSQLRepository:
    """Plain SQLAlchemy repository querying the officers table directly."""

    def __init__(self):
        pass

    async def find_by_id(self, officer_id: str | uuid.UUID, session: AsyncSession) -> Optional[Officer]:
        """Retrieves an officer by UUID."""
        if isinstance(officer_id, str):
            officer_id = uuid.UUID(officer_id)
        result = await session.execute(
            select(Officer).where(Officer.id == officer_id)
        )
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str, session: AsyncSession) -> Optional[Officer]:
        """Retrieves an officer by email."""
        result = await session.execute(
            select(Officer).where(Officer.email == email)
        )
        return result.scalar_one_or_none()

    async def create_with_password(self, data: Dict[str, Any], hashed_password: str, session: AsyncSession) -> Officer:
        """Creates a new officer with an optional hashed password."""
        officer = Officer(**data)
        officer.hashed_password = hashed_password
        session.add(officer)
        await session.commit()
        await session.refresh(officer)
        return officer

    async def update_password(self, officer_id: str, hashed_password: str, session: AsyncSession) -> Optional[Officer]:
        """Updates the hashed password for an officer."""
        officer = await self.find_by_id(officer_id, session)
        if not officer:
            return None
        officer.hashed_password = hashed_password
        session.add(officer)
        await session.commit()
        await session.refresh(officer)
        return officer
