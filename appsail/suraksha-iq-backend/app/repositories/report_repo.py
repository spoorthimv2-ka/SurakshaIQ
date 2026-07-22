from typing import List, Dict, Any, Optional
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError
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
            offset_val = offset if offset > 0 else 1
            query = f"SELECT * FROM {self.table_name} ORDER BY {sort_by} {sort_order} LIMIT {offset_val}, {limit}"
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching recent reports: {e}")
            raise RepositoryError(f"Failed to fetch recent reports: {e}")

    async def find_by_type(self, report_type: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieves reports by type."""
        try:
            offset_val = offset if offset > 0 else 1
            query = f"SELECT * FROM {self.table_name} WHERE report_type = '{report_type}' ORDER BY CREATEDTIME DESC LIMIT {offset_val}, {limit}"
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching reports of type {report_type}: {e}")
            raise RepositoryError(f"Failed to fetch reports by type: {e}")

    async def search(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs a text search on report name or type."""
        try:
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE name LIKE '%{search_term}%' "
                f"OR report_type LIKE '%{search_term}%' "
                f"LIMIT {limit}"
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
            query = f"SELECT COUNT(ROWID) FROM {self.table_name} WHERE report_type = '{report_type}'"
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
            today = "CURRENT_DATE()"
            query = f"SELECT COUNT(ROWID) FROM {self.table_name} WHERE CREATEDTIME >= {today}"
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
