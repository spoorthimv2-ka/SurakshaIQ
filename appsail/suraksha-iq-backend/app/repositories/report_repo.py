from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError, DataValidationError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger

class ReportRepository(BaseCatalystRepository):
    """
    Repository for Report entity backed by Catalyst Data Store.
    """
    def __init__(self, request):
        super().__init__(request, table_name="Report")

    async def find_recent(self, limit: int = 10, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves recent reports."""
        try:
            self._validate_column(self.table_name, sort_by)
            if sort_order.upper() not in ("ASC", "DESC"):
                raise DataValidationError("sort_order must be ASC or DESC")
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name} "
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
            logger.error(f"Error fetching recent reports: {e}")
            raise RepositoryError(f"Failed to fetch recent reports: {e}")

    async def find_all(self, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves all reports with pagination."""
        try:
            self._validate_column(self.table_name, sort_by)
            if sort_order.upper() not in ("ASC", "DESC"):
                raise DataValidationError("sort_order must be ASC or DESC")
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name} "
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
            logger.error(f"Error fetching reports: {e}")
            raise RepositoryError(f"Failed to fetch reports: {e}")

    async def find_by_type(self, report_type: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieves reports by type."""
        try:
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE report_type = {self._zcql_escape(report_type)} "
                f"ORDER BY CREATEDTIME DESC "
                f"LIMIT {offset_val}, {int(limit)}"
            )
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching reports of type {report_type}: {e}")
            raise RepositoryError(f"Failed to fetch reports by type: {e}")

    async def find_by_id(self, row_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a report by ROWID."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE ROWID = {self._zcql_escape(row_id)} LIMIT 1"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                return result[0].get(self.table_name)
            return None
        except CatalystError as e:
            logger.error(f"Error fetching report {row_id}: {e}")
            raise RepositoryError(f"Failed to fetch report: {e}")

    async def search(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs a text search on report name or type."""
        try:
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE name LIKE {self._zcql_like(search_term)} "
                f"OR report_type LIKE {self._zcql_like(search_term)} "
                f"LIMIT {int(limit)}"
            )
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error searching reports with term '{search_term}': {e}")
            raise RepositoryError(f"Failed to search reports: {e}")

    async def count_by_type(self, report_type: str) -> int:
        """Counts reports by type."""
        try:
            query = f"SELECT COUNT(ROWID) FROM {self.table_name} WHERE report_type = {self._zcql_escape(report_type)}"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                first_row = result[0]
                for table_data in first_row.values():
                    for val in table_data.values():
                        if isinstance(val, (int, float, str)) and str(val).isdigit():
                            return int(val)
            return 0
        except CatalystError as e:
            logger.error(f"Error counting reports of type {report_type}: {e}")
            raise RepositoryError(f"Failed to count reports by type: {e}")

    async def count_today(self) -> int:
        """Counts reports created today."""
        try:
            query = f"SELECT COUNT(ROWID) FROM {self.table_name} WHERE CREATEDTIME >= CURRENT_DATE()"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                first_row = result[0]
                for table_data in first_row.values():
                    for val in table_data.values():
                        if isinstance(val, (int, float, str)) and str(val).isdigit():
                            return int(val)
            return 0
        except CatalystError as e:
            logger.error(f"Error counting today's reports: {e}")
            raise RepositoryError(f"Failed to count today's reports: {e}")

    async def count(self) -> int:
        """Counts all reports."""
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
            logger.error(f"Error counting reports: {e}")
            raise RepositoryError(f"Failed to count reports: {e}")
