from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.user_repo import UserRepository
from app.core.logger import logger

class UserService:
    """Service layer for User entity."""
    
    def __init__(self, request: Request, repo: UserRepository):
        self.request = request
        self.repo = repo

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new User."""
        logger.info(f"Creating User with data: {data}")
        return await self.repo.create(data)

    async def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing User."""
        logger.info(f"Updating User {id}")
        return await self.repo.update(id, data)

    async def delete(self, id: str) -> bool:
        """Deletes a User."""
        logger.info(f"Deleting User {id}")
        return await self.repo.delete(id)

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a User by ID."""
        logger.info(f"Fetching User {id}")
        return await self.repo.find_by_id(id)

    async def get_all(self, limit: int = 100, next_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves all Users."""
        logger.info("Fetching all Users")
        return await self.repo.find_all(limit, next_token)

    async def exists(self, column: str, value: Any) -> bool:
        """Checks if a User exists."""
        logger.info(f"Checking if User exists where {column}={value}")
        return await self.repo.exists(column, value)

    async def count(self) -> int:
        """Counts all Users."""
        logger.info("Counting all Users")
        return await self.repo.count()
