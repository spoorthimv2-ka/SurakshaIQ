from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.criminal_repo import CriminalRepository
from app.core.logger import logger
from app.core.exceptions import DataValidationError, RepositoryError

class CriminalService:
    """Service layer for Criminal entity."""
    
    def __init__(self, request: Request, repo: CriminalRepository):
        self.request = request
        self.repo = repo

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new Criminal."""
        logger.info(f"Creating Criminal with data: {data}")
        return await self.repo.create(data)

    async def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing Criminal."""
        logger.info(f"Updating Criminal {id}")
        return await self.repo.update(id, data)

    async def delete(self, id: str) -> bool:
        """Deletes a Criminal."""
        logger.info(f"Deleting Criminal {id}")
        return await self.repo.delete(id)

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a Criminal by ID."""
        logger.info(f"Fetching Criminal {id}")
        return await self.repo.find_by_id(id)

    async def get_all(self, limit: int = 100, next_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves all Criminals."""
        logger.info("Fetching all Criminals")
        return await self.repo.find_all(limit, next_token)

    async def exists(self, column: str, value: Any) -> bool:
        """Checks if a Criminal exists."""
        logger.info(f"Checking if Criminal exists where {column}={value}")
        return await self.repo.exists(column, value)

    async def count(self) -> int:
        """Counts all Criminals."""
        logger.info("Counting all Criminals")
        return await self.repo.count()

    async def find_active(self, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves active criminals with pagination."""
        logger.info("Fetching active Criminals")
        return await self.repo.find_active(limit, offset, sort_by, sort_order)

    async def search(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs a text search on criminal name or alias."""
        logger.info(f"Searching Criminals with term: {search_term}")
        return await self.repo.search(search_term, limit)
