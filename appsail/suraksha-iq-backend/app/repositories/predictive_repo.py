from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger


class PredictiveRepository(BaseCatalystRepository):
    """
    Repository for predictive intelligence aggregations backed by Catalyst Data Store.
    Reuses existing crime, FIR, hotspot, district, station, and criminal data.
    """

    def __init__(self, request: Request):
        super().__init__(request, table_name="Crime")

    async def get_predictive_data(self, limit: int = 2000) -> Dict[str, Any]:
        """Retrieves raw data for predictive analysis."""
        try:
            crimes = await self._fetch_crimes(limit)
            firs = await self._fetch_firs(limit)
            districts = await self._fetch_districts(limit)
            stations = await self._fetch_stations(limit)
            criminals = await self._fetch_criminals(limit)
            hotspots = await self._fetch_hotspots(limit)
            return {
                "crimes": crimes,
                "firs": firs,
                "districts": districts,
                "stations": stations,
                "criminals": criminals,
                "hotspots": hotspots,
            }
        except CatalystError as e:
            logger.error(f"Error fetching predictive data: {e}")
            raise RepositoryError(f"Failed to fetch predictive data: {e}")

    async def _fetch_crimes(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM Crime LIMIT {int(limit)}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "Crime" in item:
                rows.append(item["Crime"])
        return rows

    async def _fetch_firs(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM FIR LIMIT {int(limit)}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "FIR" in item:
                rows.append(item["FIR"])
        return rows

    async def _fetch_districts(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM District LIMIT {int(limit)}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "District" in item:
                rows.append(item["District"])
        return rows

    async def _fetch_stations(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM PoliceStation LIMIT {int(limit)}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "PoliceStation" in item:
                rows.append(item["PoliceStation"])
        return rows

    async def _fetch_criminals(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM Criminal LIMIT {int(limit)}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "Criminal" in item:
                rows.append(item["Criminal"])
        return rows

    async def _fetch_hotspots(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM CrimeHotspotCluster LIMIT {int(limit)}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "CrimeHotspotCluster" in item:
                rows.append(item["CrimeHotspotCluster"])
        return rows
