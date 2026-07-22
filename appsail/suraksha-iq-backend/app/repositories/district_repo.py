from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError
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
            query = f"SELECT * FROM {self.table_name} WHERE code = '{code}' LIMIT 1"
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
            # Note: Catalyst ZCQL offset starts at 1, but limit/offset syntax might vary.
            # Typical ZCQL: LIMIT <offset>, <limit> or LIMIT <limit> OFFSET <offset>
            # Assuming standard ZCQL pagination: LIMIT offset, limit (e.g. LIMIT 1, 10)
            offset_val = offset if offset > 0 else 1
            query = f"SELECT * FROM {self.table_name} WHERE status = 'ACTIVE' ORDER BY {sort_by} {sort_order} LIMIT {offset_val}, {limit}"
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching active districts: {e}")
            raise RepositoryError(f"Failed to fetch active districts: {e}")

    async def search(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs a text search on district name or code."""
        try:
            # ZCQL LIKE operator
            query = f"SELECT * FROM {self.table_name} WHERE name LIKE '%{search_term}%' OR code LIKE '%{search_term}%' LIMIT {limit}"
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error searching districts with term '{search_term}': {e}")
            raise RepositoryError(f"Failed to search districts: {e}")
