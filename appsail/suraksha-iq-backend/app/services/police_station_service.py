from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.police_station_repo import PoliceStationRepository
from app.core.logger import logger

class PoliceStationService:
    """Service layer for PoliceStation entity."""
    
    def __init__(self, request: Request, repo: PoliceStationRepository):
        self.request = request
        self.repo = repo

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new Police Station."""
        logger.info(f"Creating Police Station with data: {data}")
        return await self.repo.create(data)

    async def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing Police Station."""
        logger.info(f"Updating Police Station {id}")
        return await self.repo.update(id, data)

    async def delete(self, id: str) -> bool:
        """Deletes a Police Station."""
        logger.info(f"Deleting Police Station {id}")
        return await self.repo.delete(id)

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a Police Station by ID."""
        logger.info(f"Fetching Police Station {id}")
        return await self.repo.find_by_id(id)

    async def get_all(self, limit: int = 100, next_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves all Police Stations."""
        logger.info("Fetching all Police Stations")
        return await self.repo.find_all(limit, next_token)

    async def exists(self, column: str, value: Any) -> bool:
        """Checks if a Police Station exists."""
        logger.info(f"Checking if Police Station exists where {column}={value}")
        return await self.repo.exists(column, value)

    async def count(self) -> int:
        """Counts all Police Stations."""
        logger.info("Counting all Police Stations")
        return await self.repo.count()

    async def find_by_district(self, district_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieves all police stations for a specific district."""
        logger.info(f"Fetching Police Stations for district {district_id}")
        return await self.repo.find_by_district(district_id, limit, offset)

    async def find_active(self, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves active police stations with pagination."""
        logger.info("Fetching active Police Stations")
        return await self.repo.find_active(limit, offset, sort_by, sort_order)

    async def search(self, search_term: str, district_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs a text search on station name or code, optionally scoped to a district."""
        logger.info(f"Searching Police Stations with term: {search_term}")
        return await self.repo.search(search_term, district_id, limit)
