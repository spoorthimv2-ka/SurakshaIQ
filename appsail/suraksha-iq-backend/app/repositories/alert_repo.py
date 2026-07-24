from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError, DataValidationError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger

class AlertRepository(BaseCatalystRepository):
    """
    Repository for Alert entity backed by Catalyst Data Store.
    """
    def __init__(self, request: Request):
        super().__init__(request, table_name="Alert")

    async def find_by_district(self, district_id: str, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves alerts scoped to a specific district or statewide (district_id is null)."""
        try:
            self._validate_column(self.table_name, sort_by)
            if sort_order.upper() not in ("ASC", "DESC"):
                raise DataValidationError("sort_order must be ASC or DESC")
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE district_id = {self._zcql_escape(district_id)} OR district_id IS NULL "
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
            logger.error(f"Error fetching alerts for district {district_id}: {e}")
            raise RepositoryError(f"Failed to fetch district alerts: {e}")

    async def find_active(self, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC", district_id: Optional[str] = None, station_id: Optional[str] = None, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves active alerts with optional scoping filters."""
        try:
            self._validate_column(self.table_name, sort_by)
            if sort_order.upper() not in ("ASC", "DESC"):
                raise DataValidationError("sort_order must be ASC or DESC")
            clauses = [f"status = {self._zcql_escape('ACTIVE')}"]
            if district_id:
                clauses.append(f"district_id = {self._zcql_escape(district_id)}")
            if station_id:
                clauses.append(f"station_id = {self._zcql_escape(station_id)}")
            if severity:
                clauses.append(f"severity = {self._zcql_escape(severity)}")
            where = f" WHERE {' AND '.join(clauses)}"
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name}{where} "
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
            logger.error(f"Error fetching active alerts: {e}")
            raise RepositoryError(f"Failed to fetch active alerts: {e}")

    async def find_by_status(self, status: str, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC", district_id: Optional[str] = None, station_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves alerts by status with optional scoping filters."""
        try:
            self._validate_column(self.table_name, sort_by)
            if sort_order.upper() not in ("ASC", "DESC"):
                raise DataValidationError("sort_order must be ASC or DESC")
            clauses = [f"status = {self._zcql_escape(status)}"]
            if district_id:
                clauses.append(f"district_id = {self._zcql_escape(district_id)}")
            if station_id:
                clauses.append(f"station_id = {self._zcql_escape(station_id)}")
            where = f" WHERE {' AND '.join(clauses)}"
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name}{where} "
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
            logger.error(f"Error fetching alerts with status {status}: {e}")
            raise RepositoryError(f"Failed to fetch alerts by status: {e}")

    async def count_by_status(self, status: str) -> int:
        """Counts alerts by status."""
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
            logger.error(f"Error counting alerts with status {status}: {e}")
            raise RepositoryError(f"Failed to count alerts by status: {e}")

    async def count_by_severity(self, severity: str) -> int:
        """Counts alerts by severity."""
        try:
            query = f"SELECT COUNT(ROWID) FROM {self.table_name} WHERE severity = {self._zcql_escape(severity)}"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                first_row = result[0]
                for table_data in first_row.values():
                    for val in table_data.values():
                        if isinstance(val, (int, float, str)) and str(val).isdigit():
                            return int(val)
            return 0
        except CatalystError as e:
            logger.error(f"Error counting alerts with severity {severity}: {e}")
            raise RepositoryError(f"Failed to count alerts by severity: {e}")

    async def count(self) -> int:
        """Counts all alerts."""
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
            logger.error(f"Error counting alerts: {e}")
            raise RepositoryError(f"Failed to count alerts: {e}")
