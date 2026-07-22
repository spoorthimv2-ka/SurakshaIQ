from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger

class OfficerRepository(BaseCatalystRepository):
    """
    Repository for Officer entity backed by Catalyst Data Store.
    """
    def __init__(self, request: Request):
        super().__init__(request, table_name="Officer")

    async def find_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an officer profile by their associated user ID."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE user_id = '{user_id}' LIMIT 1"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                return result[0].get(self.table_name)
            return None
        except CatalystError as e:
            logger.error(f"Error fetching officer by user ID {user_id}: {e}")
            raise RepositoryError(f"Failed to fetch officer by user ID: {e}")

    async def find_by_station(self, station_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieves officers assigned to a specific police station."""
        try:
            offset_val = offset if offset > 0 else 1
            query = f"SELECT * FROM {self.table_name} WHERE station_id = '{station_id}' LIMIT {offset_val}, {limit}"
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching officers for station {station_id}: {e}")
            raise RepositoryError(f"Failed to fetch station officers: {e}")

    async def find_active(self, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves active officers with pagination."""
        try:
            offset_val = offset if offset > 0 else 1
            query = f"SELECT * FROM {self.table_name} WHERE status = 'ACTIVE' ORDER BY {sort_by} {sort_order} LIMIT {offset_val}, {limit}"
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching active officers: {e}")
            raise RepositoryError(f"Failed to fetch active officers: {e}")

    async def search(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs a text search on officer name, badge number, or email."""
        try:
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE name LIKE '%{search_term}%' "
                f"OR badge_number LIKE '%{search_term}%' "
                f"OR email LIKE '%{search_term}%' "
                f"LIMIT {limit}"
            )
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error searching officers with term '{search_term}': {e}")
            raise RepositoryError(f"Failed to search officers: {e}")
