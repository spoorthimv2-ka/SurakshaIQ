from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError, DataValidationError
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
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE user_id = {self._zcql_escape(user_id)} "
                f"OR catalyst_user_id = {self._zcql_escape(user_id)} "
                f"LIMIT 1"
            )
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
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE station_id = {self._zcql_escape(station_id)} "
                f"LIMIT {offset_val}, {int(limit)}"
            )
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
            self._validate_column(self.table_name, sort_by)
            if sort_order.upper() not in ("ASC", "DESC"):
                raise DataValidationError("sort_order must be ASC or DESC")
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE status = {self._zcql_escape('ACTIVE')} "
                f"ORDER BY {sort_by} {sort_order.upper()} "
                f"LIMIT {offset_val}, {int(limit)}"
            )
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching active officers: {e}")
            raise RepositoryError(f"Failed to fetch active officers: {e}")

    async def find_by_id(self, row_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an officer by ROWID."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE ROWID = {self._zcql_escape(row_id)} LIMIT 1"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                return result[0].get(self.table_name)
            return None
        except CatalystError as e:
            logger.error(f"Error fetching officer {row_id}: {e}")
            raise RepositoryError(f"Failed to fetch officer: {e}")

    async def search(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs a text search on officer name, badge number, or email."""
        try:
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE name LIKE {self._zcql_like(search_term)} "
                f"OR badge_number LIKE {self._zcql_like(search_term)} "
                f"OR email LIKE {self._zcql_like(search_term)} "
                f"LIMIT {int(limit)}"
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

    async def count(self) -> int:
        """Counts all officers."""
        try:
            query = f"SELECT COUNT(ROWID) FROM {self.table_name}"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                first_row = result[0]
                for table_data in first_row.values():
                    for val in table_data.values():
                        if isinstance(val, (int, float, str)) and str(val).isdigit():
                            return int(val)
            return 0
        except CatalystError as e:
            logger.error(f"Error counting officers: {e}")
            raise RepositoryError(f"Failed to count officers: {e}")
