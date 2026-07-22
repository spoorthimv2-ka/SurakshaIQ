from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.district_repo import DistrictRepository
from app.core.logger import logger

class DistrictService:
    """Service layer for District entity."""
    
    def __init__(self, request: Request, repo: DistrictRepository):
        self.request = request
        self.repo = repo

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new District."""
        logger.info(f"Creating District with data: {data}")
        return await self.repo.create(data)

    async def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing District."""
        logger.info(f"Updating District {id}")
        return await self.repo.update(id, data)

    async def delete(self, id: str) -> bool:
        """Deletes a District."""
        logger.info(f"Deleting District {id}")
        return await self.repo.delete(id)

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a District by ID."""
        logger.info(f"Fetching District {id}")
        return await self.repo.find_by_id(id)

    async def get_all(self, limit: int = 100, next_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves all Districts."""
        logger.info("Fetching all Districts")
        return await self.repo.find_all(limit, next_token)

    async def exists(self, column: str, value: Any) -> bool:
        """Checks if a District exists."""
        logger.info(f"Checking if District exists where {column}={value}")
        return await self.repo.exists(column, value)

    async def count(self) -> int:
        """Counts all Districts."""
        logger.info("Counting all Districts")
        return await self.repo.count()

    async def find_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Finds a district by its unique code."""
        logger.info(f"Fetching District by code {code}")
        return await self.repo.find_by_code(code)

    async def find_active(self, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves active districts with pagination."""
        logger.info("Fetching active Districts")
        return await self.repo.find_active(limit, offset, sort_by, sort_order)

    async def search(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs a text search on district name or code."""
        logger.info(f"Searching Districts with term: {search_term}")
        return await self.repo.search(search_term, limit)
