from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError
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
            offset_val = offset if offset > 0 else 1
            query = f"SELECT * FROM {self.table_name} WHERE district_id = '{district_id}' OR district_id IS NULL ORDER BY {sort_by} {sort_order} LIMIT {offset_val}, {limit}"
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching alerts for district {district_id}: {e}")
            raise RepositoryError(f"Failed to fetch district alerts: {e}")

    async def find_active(self, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves active alerts with pagination."""
        try:
            offset_val = offset if offset > 0 else 1
            query = f"SELECT * FROM {self.table_name} WHERE status = 'ACTIVE' ORDER BY {sort_by} {sort_order} LIMIT {offset_val}, {limit}"
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching active alerts: {e}")
            raise RepositoryError(f"Failed to fetch active alerts: {e}")

    async def find_by_status(self, status: str, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves alerts by status."""
        try:
            offset_val = offset if offset > 0 else 1
            query = f"SELECT * FROM {self.table_name} WHERE status = '{status}' ORDER BY {sort_by} {sort_order} LIMIT {offset_val}, {limit}"
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
            query = f"SELECT COUNT(ROWID) FROM {self.table_name} WHERE status = '{status}'"
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
            query = f"SELECT COUNT(ROWID) FROM {self.table_name} WHERE severity = '{severity}'"
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
