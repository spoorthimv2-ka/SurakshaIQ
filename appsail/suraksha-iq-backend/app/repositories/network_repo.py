from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger

class NetworkRepository(BaseCatalystRepository):
    """
    Repository for network graph aggregations backed by Catalyst Data Store.
    """

    def __init__(self, request: Request):
        super().__init__(request, table_name="Crime")

    async def get_network_data(self, limit: int = 500) -> Dict[str, Any]:
        """Retrieves raw data for network graph construction."""
        try:
            crimes = await self._fetch_crimes(limit)
            firs = await self._fetch_firs(limit)
            criminals = await self._fetch_criminals(limit)
            districts = await self._fetch_districts(limit)
            stations = await self._fetch_stations(limit)
            officers = await self._fetch_officers(limit)
            return {
                "crimes": crimes,
                "firs": firs,
                "criminals": criminals,
                "districts": districts,
                "stations": stations,
                "officers": officers,
            }
        except CatalystError as e:
            logger.error(f"Error fetching network data: {e}")
            raise RepositoryError(f"Failed to fetch network data: {e}")

    async def _fetch_crimes(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM Crime LIMIT {limit}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "Crime" in item:
                rows.append(item["Crime"])
        return rows

    async def _fetch_firs(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM FIR LIMIT {limit}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "FIR" in item:
                rows.append(item["FIR"])
        return rows

    async def _fetch_criminals(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM Criminal LIMIT {limit}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "Criminal" in item:
                rows.append(item["Criminal"])
        return rows

    async def _fetch_districts(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM District LIMIT {limit}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "District" in item:
                rows.append(item["District"])
        return rows

    async def _fetch_stations(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM PoliceStation LIMIT {limit}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "PoliceStation" in item:
                rows.append(item["PoliceStation"])
        return rows

    async def _fetch_officers(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM Officer LIMIT {limit}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "Officer" in item:
                rows.append(item["Officer"])
        return rows
