from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger

class HotspotRepository(BaseCatalystRepository):
    """
    Repository for hotspot aggregations backed by Catalyst Data Store.
    """

    def __init__(self, request: Request):
        super().__init__(request, table_name="Crime")

    async def count_by_district(self, district_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
        """Counts crimes in a district within an optional date range."""
        try:
            query = f"SELECT COUNT(ROWID) FROM {self.table_name} WHERE district_id = '{district_id}'"
            if date_from:
                query += f" AND CREATEDTIME >= '{date_from}'"
            if date_to:
                query += f" AND CREATEDTIME <= '{date_to}'"
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

    async def count_by_station(self, station_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
        """Counts crimes at a police station within an optional date range."""
        try:
            query = f"SELECT COUNT(ROWID) FROM {self.table_name} WHERE station_id = '{station_id}'"
            if date_from:
                query += f" AND CREATEDTIME >= '{date_from}'"
            if date_to:
                query += f" AND CREATEDTIME <= '{date_to}'"
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

    async def find_recent_by_district(self, district_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieves recent crimes for a district."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE district_id = '{district_id}' ORDER BY CREATEDTIME DESC LIMIT {limit}"
            result = self.zcql.execute_query(query)
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching recent crimes for district {district_id}: {e}")
            raise RepositoryError(f"Failed to fetch district recent crimes: {e}")

    async def find_recent_by_station(self, station_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieves recent crimes for a police station."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE station_id = '{station_id}' ORDER BY CREATEDTIME DESC LIMIT {limit}"
            result = self.zcql.execute_query(query)
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching recent crimes for station {station_id}: {e}")
            raise RepositoryError(f"Failed to fetch station recent crimes: {e}")

    async def find_filtered(
        self,
        district_id: Optional[str] = None,
        station_id: Optional[str] = None,
        crime_type: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Retrieves crimes with optional filters."""
        try:
            offset_val = offset if offset > 0 else 1
            query = f"SELECT * FROM {self.table_name} WHERE 1=1"
            if district_id:
                query += f" AND district_id = '{district_id}'"
            if station_id:
                query += f" AND station_id = '{station_id}'"
            if crime_type:
                query += f" AND crime_type = '{crime_type}'"
            if status:
                query += f" AND status = '{status}'"
            if date_from:
                query += f" AND CREATEDTIME >= '{date_from}'"
            if date_to:
                query += f" AND CREATEDTIME <= '{date_to}'"
            query += f" ORDER BY CREATEDTIME DESC LIMIT {offset_val}, {limit}"
            result = self.zcql.execute_query(query)
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching filtered crimes: {e}")
            raise RepositoryError(f"Failed to fetch filtered crimes: {e}")
