from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError, DataValidationError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger

class DistrictRepository(BaseCatalystRepository):
    """
    Repository for District entity backed by Catalyst Data Store.
    """
    def __init__(self, request: Request):
        super().__init__(request, table_name="District")

    async def find_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Finds a district by its unique code."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE code = {self._zcql_escape(code)} LIMIT 1"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                return result[0].get(self.table_name)
            return None
        except CatalystError as e:
            logger.error(f"Error finding district by code '{code}': {e}")
            raise RepositoryError(f"Failed to find district: {e}")

    async def find_active(self, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves active districts with pagination."""
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
            logger.error(f"Error fetching active districts: {e}")
            raise RepositoryError(f"Failed to fetch active districts: {e}")

    async def find_by_id(self, row_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a district by ROWID."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE ROWID = {self._zcql_escape(row_id)} LIMIT 1"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                return result[0].get(self.table_name)
            return None
        except CatalystError as e:
            logger.error(f"Error fetching district {row_id}: {e}")
            raise RepositoryError(f"Failed to fetch district: {e}")

    async def search(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs a text search on district name or code."""
        try:
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE name LIKE {self._zcql_like(search_term)} "
                f"OR code LIKE {self._zcql_like(search_term)} "
                f"LIMIT {int(limit)}"
            )
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error searching districts with term '{search_term}': {e}")
            raise RepositoryError(f"Failed to search districts: {e}")

    async def count(self) -> int:
        """Counts all districts."""
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
            logger.error(f"Error counting districts: {e}")
            raise RepositoryError(f"Failed to count districts: {e}")
