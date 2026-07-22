from typing import List, Dict, Any, Optional
from fastapi import Request

from app.repositories.officer_repo import OfficerRepository
from app.core.logger import logger


class OfficerService:
    """Service layer orchestrating Officer operations."""
    
    def __init__(self, request: Request, repo: OfficerRepository):
        self.request = request
        self.repo = repo

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new Officer."""
        logger.info(f"Creating Officer with data: {data}")
        return await self.repo.create(data)

    async def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing Officer."""
        logger.info(f"Updating Officer {id}")
        return await self.repo.update(id, data)

    async def delete(self, id: str) -> bool:
        """Deletes an Officer."""
        logger.info(f"Deleting Officer {id}")
        return await self.repo.delete(id)

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an Officer by ID."""
        logger.info(f"Fetching Officer {id}")
        return await self.repo.find_by_id(id)

    async def get_all(self, limit: int = 100, next_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves all Officers."""
        logger.info("Fetching all Officers")
        return await self.repo.find_all(limit, next_token)

    async def exists(self, column: str, value: Any) -> bool:
        """Checks if an Officer exists."""
        logger.info(f"Checking if Officer exists where {column}={value}")
        return await self.repo.exists(column, value)

    async def count(self) -> int:
        """Counts all Officers."""
        logger.info("Counting all Officers")
        return await self.repo.count()

    async def sync_catalyst_identity(self, catalyst_identity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Looks up an officer by their Catalyst ID. If they don't exist, provisions a new record.
        """
        catalyst_id = str(catalyst_identity.get("user_id"))
        email = str(catalyst_identity.get("email_id"))
        
        first_name = catalyst_identity.get("first_name", "")
        last_name = catalyst_identity.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip() or "Unknown Officer"
        
        role_details = catalyst_identity.get("role_details", {})
        catalyst_role = role_details.get("role_name", "STATION_HOUSE_OFFICER")

        # 1. Lookup existing
        officer = await self.repo.find_by_user_id(catalyst_id)
        if officer:
            return officer
            
        # 2. First-login provisioning
        new_officer_data = {
            "user_id": catalyst_id,
            "name": full_name,
            "email": email,
            "role": catalyst_role,
            "badge_number": f"AUTO-{catalyst_id[:8]}",
            "status": "ACTIVE",
        }
        
        created_officer = await self.repo.create(new_officer_data)
        logger.info(f"Provisioned new officer for Catalyst user {catalyst_id}")
        return created_officer
