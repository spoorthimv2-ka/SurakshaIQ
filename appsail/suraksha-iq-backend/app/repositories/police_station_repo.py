from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError
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
            offset_val = offset if offset > 0 else 1
            query = f"SELECT * FROM {self.table_name} WHERE district_id = '{district_id}' LIMIT {offset_val}, {limit}"
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
            offset_val = offset if offset > 0 else 1
            query = f"SELECT * FROM {self.table_name} WHERE status = 'ACTIVE' ORDER BY {sort_by} {sort_order} LIMIT {offset_val}, {limit}"
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching active police stations: {e}")
            raise RepositoryError(f"Failed to fetch active police stations: {e}")

    async def search(self, search_term: str, district_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs a text search on station name or code, optionally scoped to a district."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE (name LIKE '%{search_term}%' OR code LIKE '%{search_term}%')"
            if district_id:
                query += f" AND district_id = '{district_id}'"
            query += f" LIMIT {limit}"
            
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error searching police stations with term '{search_term}': {e}")
            raise RepositoryError(f"Failed to search police stations: {e}")
