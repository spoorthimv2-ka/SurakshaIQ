from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError, DataValidationError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger

class PredictiveRiskRepository(BaseCatalystRepository):
    """
    Repository for predictive risk aggregations backed by Catalyst Data Store.
    """
    def __init__(self, request: Request):
        super().__init__(request, table_name="Crime")

    async def get_risk_data(self, limit: int = 1000) -> Dict[str, Any]:
        """Retrieves aggregated risk data from multiple tables."""
        try:
            crimes = await self._fetch_crimes(limit)
            firs = await self._fetch_firs(limit)
            criminals = await self._fetch_criminals(limit)
            districts = await self._fetch_districts(limit)
            stations = await self._fetch_stations(limit)
            return {
                "crimes": crimes,
                "firs": firs,
                "criminals": criminals,
                "districts": districts,
                "stations": stations,
            }
        except CatalystError as e:
            logger.error(f"Error fetching risk data: {e}")
            raise RepositoryError(f"Failed to fetch risk data: {e}")

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

    async def _fetch_criminals(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM Criminal LIMIT {int(limit)}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "Criminal" in item:
                rows.append(item["Criminal"])
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

    async def count_crimes_by_district(self, district_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
        """Counts crimes in a district within an optional date range."""
        try:
            clauses = [f"district_id = {self._zcql_escape(district_id)}"]
            if date_from:
                clauses.append(f"CREATEDTIME >= {self._zcql_escape(date_from)}")
            if date_to:
                clauses.append(f"CREATEDTIME <= {self._zcql_escape(date_to)}")
            where = f" WHERE {' AND '.join(clauses)}"
            query = f"SELECT COUNT(ROWID) FROM Crime{where}"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                first_row = result[0]
                for table_data in first_row.values():
                    for val in table_data.values():
                        if isinstance(val, (int, float, str)) and str(val).isdigit():
                            return int(val)
            return 0
        except CatalystError as e:
            logger.error(f"Error counting crimes for district {district_id}: {e}")
            raise RepositoryError(f"Failed to count district crimes: {e}")

    async def count_crimes_by_station(self, station_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
        """Counts crimes at a police station within an optional date range."""
        try:
            clauses = [f"station_id = {self._zcql_escape(station_id)}"]
            if date_from:
                clauses.append(f"CREATEDTIME >= {self._zcql_escape(date_from)}")
            if date_to:
                clauses.append(f"CREATEDTIME <= {self._zcql_escape(date_to)}")
            where = f" WHERE {' AND '.join(clauses)}"
            query = f"SELECT COUNT(ROWID) FROM Crime{where}"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                first_row = result[0]
                for table_data in first_row.values():
                    for val in table_data.values():
                        if isinstance(val, (int, float, str)) and str(val).isdigit():
                            return int(val)
            return 0
        except CatalystError as e:
            logger.error(f"Error counting crimes for station {station_id}: {e}")
            raise RepositoryError(f"Failed to count station crimes: {e}")

    async def count_firs_by_district(self, district_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
        """Counts FIRs in a district."""
        try:
            clauses = [f"district_id = {self._zcql_escape(district_id)}"]
            if date_from:
                clauses.append(f"CREATEDTIME >= {self._zcql_escape(date_from)}")
            if date_to:
                clauses.append(f"CREATEDTIME <= {self._zcql_escape(date_to)}")
            where = f" WHERE {' AND '.join(clauses)}"
            query = f"SELECT COUNT(ROWID) FROM FIR{where}"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                first_row = result[0]
                for table_data in first_row.values():
                    for val in table_data.values():
                        if isinstance(val, (int, float, str)) and str(val).isdigit():
                            return int(val)
            return 0
        except CatalystError as e:
            logger.error(f"Error counting FIRs for district {district_id}: {e}")
            raise RepositoryError(f"Failed to count district FIRs: {e}")

    async def count_firs_by_station(self, station_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
        """Counts FIRs at a police station."""
        try:
            clauses = [f"station_id = {self._zcql_escape(station_id)}"]
            if date_from:
                clauses.append(f"CREATEDTIME >= {self._zcql_escape(date_from)}")
            if date_to:
                clauses.append(f"CREATEDTIME <= {self._zcql_escape(date_to)}")
            where = f" WHERE {' AND '.join(clauses)}"
            query = f"SELECT COUNT(ROWID) FROM FIR{where}"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                first_row = result[0]
                for table_data in first_row.values():
                    for val in table_data.values():
                        if isinstance(val, (int, float, str)) and str(val).isdigit():
                            return int(val)
            return 0
        except CatalystError as e:
            logger.error(f"Error counting FIRs for station {station_id}: {e}")
            raise RepositoryError(f"Failed to count station FIRs: {e}")
