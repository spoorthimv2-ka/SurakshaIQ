from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError, DataValidationError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger

class FIRRepository(BaseCatalystRepository):
    """
    Repository for FIR entity backed by Catalyst Data Store.
    """
    def __init__(self, request: Request):
        super().__init__(request, table_name="FIR")

    async def find_by_number(self, fir_number: str) -> Optional[Dict[str, Any]]:
        """Retrieves an FIR by its unique FIR number."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE fir_number = {self._zcql_escape(fir_number)} LIMIT 1"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                return result[0].get(self.table_name)
            return None
        except CatalystError as e:
            logger.error(f"Error fetching FIR by number {fir_number}: {e}")
            raise RepositoryError(f"Failed to fetch FIR by number: {e}")

    async def find_by_station(self, station_id: str, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves FIRs scoped to a specific police station."""
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
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching FIRs for station {station_id}: {e}")
            raise RepositoryError(f"Failed to fetch station FIRs: {e}")

    async def search(self, search_term: str, station_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs a text search on FIR number or description."""
        try:
            clauses = [
                f"(fir_number LIKE {self._zcql_like(search_term)} "
                f"OR description LIKE {self._zcql_like(search_term)})"
            ]
            if station_id:
                clauses.append(f"station_id = {self._zcql_escape(station_id)}")
            query = f"SELECT * FROM {self.table_name} WHERE {' AND '.join(clauses)} LIMIT {int(limit)}"
            
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error searching FIRs with term '{search_term}': {e}")
            raise RepositoryError(f"Failed to search FIRs: {e}")

    async def find_all_with_filters(
        self,
        limit: int = 100,
        offset: int = 0,
        fir_number: Optional[str] = None,
        keyword: Optional[str] = None,
        district_id: Optional[str] = None,
        station_id: Optional[str] = None,
        officer_id: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        sort_by: str = "CREATEDTIME",
        sort_order: str = "DESC",
    ) -> List[Dict[str, Any]]:
        """Retrieves FIRs with optional filters."""
        try:
            self._validate_column(self.table_name, sort_by)
            if sort_order.upper() not in ("ASC", "DESC"):
                raise DataValidationError("sort_order must be ASC or DESC")
            clauses: List[str] = []
            
            if fir_number:
                clauses.append(f"fir_number LIKE {self._zcql_like(fir_number)}")
            if keyword:
                clauses.append(
                    f"(fir_number LIKE {self._zcql_like(keyword)} "
                    f"OR description LIKE {self._zcql_like(keyword)} "
                    f"OR sections LIKE {self._zcql_like(keyword)} "
                    f"OR summary LIKE {self._zcql_like(keyword)} "
                    f"OR victim_name LIKE {self._zcql_like(keyword)} "
                    f"OR suspect_name LIKE {self._zcql_like(keyword)} "
                    f"OR vehicle_number LIKE {self._zcql_like(keyword)} "
                    f"OR mobile_number LIKE {self._zcql_like(keyword)} "
                    f"OR ipc_sections LIKE {self._zcql_like(keyword)})"
                )
            if district_id:
                clauses.append(f"district_id = {self._zcql_escape(district_id)}")
            if station_id:
                clauses.append(f"station_id = {self._zcql_escape(station_id)}")
            if officer_id:
                clauses.append(f"officer_id = {self._zcql_escape(officer_id)}")
            if status:
                clauses.append(f"status = {self._zcql_escape(status)}")
            if date_from:
                clauses.append(f"CREATEDTIME >= {self._zcql_escape(date_from)}")
            if date_to:
                clauses.append(f"CREATEDTIME <= {self._zcql_escape(date_to)}")
            
            where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name} {where} "
                f"ORDER BY {sort_by} {sort_order.upper()} LIMIT {offset_val}, {int(limit)}"
            )
            
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching filtered FIRs: {e}")
            raise RepositoryError(f"Failed to fetch filtered FIRs: {e}")

    async def count_by_status(self, status: str) -> int:
        """Counts FIRs by status."""
        try:
            query = f"SELECT COUNT(ROWID) FROM {self.table_name} WHERE status = {self._zcql_escape(status)}"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                first_row = result[0]
                for table_data in first_row.values():
                    for val in table_data.values():
                        if isinstance(val, (int, float, str)) and str(val).isdigit():
                            return int(val)
            return 0
        except CatalystError as e:
            logger.error(f"Error counting FIRs by status {status}: {e}")
            raise RepositoryError(f"Failed to count FIRs by status: {e}")

    async def count_by_date_range(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
        """Counts FIRs within an optional date range."""
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
            logger.error(f"Error counting FIRs by date range: {e}")
            raise RepositoryError(f"Failed to count FIRs by date range: {e}")
