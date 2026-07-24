from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError, DataValidationError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger

class RepeatOffenderRepository(BaseCatalystRepository):
    """
    Repository for repeat offender aggregations backed by Catalyst Data Store.
    """
    def __init__(self, request: Request):
        super().__init__(request, table_name="Criminal")

    async def find_active(self, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC", district_id: Optional[str] = None, station_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves active criminals with optional scoping filters."""
        try:
            self._validate_column(self.table_name, sort_by)
            if sort_order.upper() not in ("ASC", "DESC"):
                raise DataValidationError("sort_order must be ASC or DESC")
            clauses = [f"status = {self._zcql_escape('ACTIVE')}"]
            if district_id:
                clauses.append(f"last_known_location = {self._zcql_escape(district_id)}")
            where = f"WHERE {' AND '.join(clauses)} "
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name} {where}"
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
            logger.error(f"Error fetching active criminals: {e}")
            raise RepositoryError(f"Failed to fetch active criminals: {e}")

    async def find_by_id(self, row_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a criminal by ROWID."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE ROWID = {self._zcql_escape(row_id)} LIMIT 1"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                return result[0].get(self.table_name)
            return None
        except CatalystError as e:
            logger.error(f"Error fetching criminal {row_id}: {e}")
            raise RepositoryError(f"Failed to fetch criminal: {e}")

    async def search(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs a text search on criminal name or alias."""
        try:
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE name LIKE {self._zcql_like(search_term)} "
                f"OR alias LIKE {self._zcql_like(search_term)} "
                f"LIMIT {int(limit)}"
            )
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error searching criminals with term '{search_term}': {e}")
            raise RepositoryError(f"Failed to search criminals: {e}")

    async def count(self) -> int:
        """Counts all criminals."""
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
            logger.error(f"Error counting criminals: {e}")
            raise RepositoryError(f"Failed to count criminals: {e}")
