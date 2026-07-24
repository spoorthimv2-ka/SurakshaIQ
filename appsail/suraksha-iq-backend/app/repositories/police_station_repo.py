from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError, DataValidationError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger

class PoliceStationRepository(BaseCatalystRepository):
    """
    Repository for PoliceStation entity backed by Catalyst Data Store.
    """
    def __init__(self, request: Request):
        super().__init__(request, table_name="PoliceStation")

    async def find_by_district(self, district_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieves all police stations for a specific district."""
        try:
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE district_id = {self._zcql_escape(district_id)} "
                f"LIMIT {offset_val}, {int(limit)}"
            )
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching police stations for district {district_id}: {e}")
            raise RepositoryError(f"Failed to fetch district stations: {e}")

    async def find_active(self, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves active police stations with pagination."""
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
            logger.error(f"Error fetching active police stations: {e}")
            raise RepositoryError(f"Failed to fetch active stations: {e}")

    async def find_by_id(self, row_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a police station by ROWID."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE ROWID = {self._zcql_escape(row_id)} LIMIT 1"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                return result[0].get(self.table_name)
            return None
        except CatalystError as e:
            logger.error(f"Error fetching police station {row_id}: {e}")
            raise RepositoryError(f"Failed to fetch station: {e}")

    async def search(self, search_term: str, district_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs a text search on station name or code, optionally scoped to a district."""
        try:
            clauses = [
                f"(name LIKE {self._zcql_like(search_term)} "
                f"OR code LIKE {self._zcql_like(search_term)})"
            ]
            if district_id:
                clauses.append(f"district_id = {self._zcql_escape(district_id)}")
            query = f"SELECT * FROM {self.table_name} WHERE {' AND '.join(clauses)} LIMIT {int(limit)}"
            
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error searching police stations with term '{search_term}': {e}")
            raise RepositoryError(f"Failed to search stations: {e}")

    async def count(self) -> int:
        """Counts all police stations."""
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
            logger.error(f"Error counting police stations: {e}")
            raise RepositoryError(f"Failed to count stations: {e}")
