from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger

class CrimeRepository(BaseCatalystRepository):
    """
    Repository for Crime entity backed by Catalyst Data Store.
    """
    def __init__(self, request: Request):
        super().__init__(request, table_name="Crime")

    async def find_by_district(self, district_id: str, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves crimes scoped to a specific district."""
        try:
            self._validate_column(self.table_name, sort_by)
            if sort_order.upper() not in ("ASC", "DESC"):
                raise DataValidationError("sort_order must be ASC or DESC")
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE district_id = {self._zcql_escape(district_id)} "
                f"ORDER BY {sort_by} {sort_order.upper()} "
                f"LIMIT {offset_val}, {int(limit)}"
            )
            result = self.zcql.execute_query(query)
            return [item[self.table_name] for item in result if self.table_name in item]
        except CatalystError as e:
            logger.error(f"Error fetching crimes for district {district_id}: {e}")
            raise RepositoryError(f"Failed to fetch district crimes: {e}")

    async def find_by_station(self, station_id: str, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves crimes scoped to a specific police station."""
        try:
            self._validate_column(self.table_name, sort_by)
            if sort_order.upper() not in ("ASC", "DESC"):
                raise DataValidationError("sort_order must be ASC or DESC")
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE station_id = {self._zcql_escape(station_id)} "
                f"ORDER BY {sort_by} {sort_order.upper()} "
                f"LIMIT {offset_val}, {int(limit)}"
            )
            result = self.zcql.execute_query(query)
            return [item[self.table_name] for item in result if self.table_name in item]
        except CatalystError as e:
            logger.error(f"Error fetching crimes for station {station_id}: {e}")
            raise RepositoryError(f"Failed to fetch station crimes: {e}")

    async def search(self, search_term: str, district_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs a text search on crime title, description, or type."""
        try:
            clauses: List[str] = [
                f"(title LIKE {self._zcql_like(search_term)} "
                f"OR description LIKE {self._zcql_like(search_term)} "
                f"OR crime_type LIKE {self._zcql_like(search_term)})"
            ]
            if district_id:
                clauses.append(f"district_id = {self._zcql_escape(district_id)}")
            query = f"SELECT * FROM {self.table_name} WHERE {' AND '.join(clauses)} LIMIT {int(limit)}"
            result = self.zcql.execute_query(query)
            return [item[self.table_name] for item in result if self.table_name in item]
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
            self._validate_column(self.table_name, sort_by)
            if sort_order.upper() not in ("ASC", "DESC"):
                raise DataValidationError("sort_order must be ASC or DESC")
            clauses: List[str] = ["1=1"]
            if keyword:
                clauses.append(
                    f"(title LIKE {self._zcql_like(keyword)} "
                    f"OR description LIKE {self._zcql_like(keyword)} "
                    f"OR crime_type LIKE {self._zcql_like(keyword)} "
                    f"OR victim_name LIKE {self._zcql_like(keyword)} "
                    f"OR suspect_name LIKE {self._zcql_like(keyword)} "
                    f"OR alias LIKE {self._zcql_like(keyword)} "
                    f"OR vehicle_number LIKE {self._zcql_like(keyword)} "
                    f"OR mobile_number LIKE {self._zcql_like(keyword)} "
                    f"OR weapon LIKE {self._zcql_like(keyword)} "
                    f"OR modus_operandi LIKE {self._zcql_like(keyword)} "
                    f"OR keywords LIKE {self._zcql_like(keyword)} "
                    f"OR ipc_sections LIKE {self._zcql_like(keyword)} "
                    f"OR location LIKE {self._zcql_like(keyword)})"
                )
            if district_id:
                clauses.append(f"district_id = {self._zcql_escape(district_id)}")
            if station_id:
                clauses.append(f"station_id = {self._zcql_escape(station_id)}")
            if crime_type:
                clauses.append(f"crime_type = {self._zcql_escape(crime_type)}")
            if status:
                clauses.append(f"status = {self._zcql_escape(status)}")
            if date_from:
                clauses.append(f"CREATEDTIME >= {self._zcql_escape(date_from)}")
            if date_to:
                clauses.append(f"CREATEDTIME <= {self._zcql_escape(date_to)}")
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name} WHERE {' AND '.join(clauses)} "
                f"ORDER BY {sort_by} {sort_order.upper()} LIMIT {offset_val}, {int(limit)}"
            )
            result = self.zcql.execute_query(query)
            return [item[self.table_name] for item in result if self.table_name in item]
        except CatalystError as e:
            logger.error(f"Error fetching filtered crimes: {e}")
            raise RepositoryError(f"Failed to fetch filtered crimes: {e}")

    async def count_by_date_range(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
        """Counts crimes within an optional date range."""
        try:
            clauses: List[str] = []
            if date_from:
                clauses.append(f"CREATEDTIME >= {self._zcql_escape(date_from)}")
            if date_to:
                clauses.append(f"CREATEDTIME <= {self._zcql_escape(date_to)}")
            where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
            query = f"SELECT COUNT(ROWID) FROM {self.table_name}{where}"
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

    async def check_duplicate(self, title: str, district_id: str, station_id: str, exclude_id: Optional[str] = None) -> bool:
        """Checks if a duplicate crime exists."""
        try:
            clauses = [
                f"title = {self._zcql_escape(title)}",
                f"district_id = {self._zcql_escape(district_id)}",
                f"station_id = {self._zcql_escape(station_id)}",
            ]
            if exclude_id:
                clauses.append(f"ROWID != {self._zcql_escape(exclude_id)}")
            query = f"SELECT ROWID FROM {self.table_name} WHERE {' AND '.join(clauses)} LIMIT 1"
            result = self.zcql.execute_query(query)
            return len(result) > 0
        except CatalystError as e:
            logger.error(f"Error checking duplicate crime: {e}")
            raise RepositoryError(f"Failed to check duplicate crime: {e}")
