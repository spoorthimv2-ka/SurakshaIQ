from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.officer import Officer
from app.schemas.officer import OfficerCreate

class OfficerRepository:
    """
    Repository for handling database operations related to Officers.
    """
    
    @staticmethod
    async def get_by_catalyst_id(session: AsyncSession, catalyst_user_id: str) -> Optional[Officer]:
        """Fetch an officer by their Zoho Catalyst user ID."""
        stmt = select(Officer).where(
            Officer.catalyst_user_id == catalyst_user_id,
            Officer.is_deleted == False
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def create(session: AsyncSession, obj_in: OfficerCreate) -> Officer:
        """Create a new officer record in the database."""
        db_obj = Officer(**obj_in.model_dump())
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj
