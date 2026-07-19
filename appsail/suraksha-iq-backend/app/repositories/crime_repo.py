from typing import List, Dict, Any, Optional
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger

class CrimeRepository(BaseCatalystRepository):
    """
    Repository for Crime entity backed by Catalyst Data Store.
    """
    def __init__(self):
        super().__init__(table_name="Crime")

    async def find_by_district(self, district_id: str, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves crimes scoped to a specific district."""
        try:
            offset_val = offset if offset > 0 else 1
            query = f"SELECT * FROM {self.table_name} WHERE district_id = '{district_id}' ORDER BY {sort_by} {sort_order} LIMIT {offset_val}, {limit}"
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching crimes for district {district_id}: {e}")
            raise RepositoryError(f"Failed to fetch district crimes: {e}")

    async def find_by_station(self, station_id: str, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves crimes scoped to a specific police station."""
        try:
            offset_val = offset if offset > 0 else 1
            query = f"SELECT * FROM {self.table_name} WHERE station_id = '{station_id}' ORDER BY {sort_by} {sort_order} LIMIT {offset_val}, {limit}"
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching crimes for station {station_id}: {e}")
            raise RepositoryError(f"Failed to fetch station crimes: {e}")

    async def search(self, search_term: str, district_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs a text search on crime title, description, or type."""
        try:
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE (title LIKE '%{search_term}%' "
                f"OR description LIKE '%{search_term}%' "
                f"OR crime_type LIKE '%{search_term}%')"
            )
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
            logger.error(f"Error searching crimes with term '{search_term}': {e}")
            raise RepositoryError(f"Failed to search crimes: {e}")

    async def find_all_with_filters(
        self,
        limit: int = 100,
        offset: int = 0,
        keyword: Optional[str] = None,
        district_id: Optional[str] = None,
        station_id: Optional[str] = None,
        crime_type: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        sort_by: str = "CREATEDTIME",
        sort_order: str = "DESC",
    ) -> List[Dict[str, Any]]:
        """Retrieves crimes with optional filters."""
        try:
            offset_val = offset if offset > 0 else 1
            query = f"SELECT * FROM {self.table_name} WHERE 1=1"
            
            if keyword:
                query += f" AND (title LIKE '%{keyword}%' OR description LIKE '%{keyword}%' OR crime_type LIKE '%{keyword}%')"
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
            
            query += f" ORDER BY {sort_by} {sort_order} LIMIT {offset_val}, {limit}"
            
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching filtered crimes: {e}")
            raise RepositoryError(f"Failed to fetch filtered crimes: {e}")

    async def count_by_date_range(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
        """Counts crimes within an optional date range."""
        try:
            query = f"SELECT COUNT(ROWID) FROM {self.table_name} WHERE 1=1"
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
            logger.error(f"Error counting crimes by date range: {e}")
            raise RepositoryError(f"Failed to count crimes by date range: {e}")
