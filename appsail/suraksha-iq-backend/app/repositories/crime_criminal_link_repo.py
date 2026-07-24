from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError, DataValidationError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger


class CrimeCriminalLinkRepository(BaseCatalystRepository):
    """
    Repository for explicit crime-offender linkage backed by Catalyst Data Store.
    """

    def __init__(self, request: Request):
        super().__init__(request, table_name="CrimeCriminalLink")

    async def create_link(self, crime_id: str, criminal_id: str, role: str = "ACCUSED", linked_by_officer_id: str = "", notes: str = "") -> Dict[str, Any]:
        """Creates a new explicit link between a crime and a criminal."""
        if not crime_id or not criminal_id:
            raise DataValidationError("crime_id and criminal_id are required")
        row_data = {
            "crime_id": crime_id,
            "criminal_id": criminal_id,
            "role": role,
            "linked_by_officer_id": linked_by_officer_id,
            "notes": notes,
            "linked_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            table = self.get_table()
            return table.insert_row(row_data)
        except CatalystError as e:
            logger.error(f"Error creating crime-criminal link: {e}")
            raise RepositoryError(f"Failed to create link: {e}")

    async def find_by_crime(self, crime_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieves all criminals linked to a specific crime."""
        try:
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE crime_id = {self._zcql_escape(crime_id)} "
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
            logger.error(f"Error fetching links for crime {crime_id}: {e}")
            raise RepositoryError(f"Failed to fetch crime links: {e}")

    async def find_by_criminal(self, criminal_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieves all crimes linked to a specific criminal."""
        try:
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE criminal_id = {self._zcql_escape(criminal_id)} "
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
            logger.error(f"Error fetching links for criminal {criminal_id}: {e}")
            raise RepositoryError(f"Failed to fetch criminal links: {e}")

    async def find_by_crime_and_criminal(self, crime_id: str, criminal_id: str) -> Optional[Dict[str, Any]]:
        """Checks if a specific crime-criminal link exists."""
        try:
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE crime_id = {self._zcql_escape(crime_id)} "
                f"AND criminal_id = {self._zcql_escape(criminal_id)} "
                f"LIMIT 1"
            )
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                return result[0].get(self.table_name)
            return None
        except CatalystError as e:
            logger.error(f"Error checking link for crime {crime_id} and criminal {criminal_id}: {e}")
            raise RepositoryError(f"Failed to check link: {e}")

    async def delete_link(self, row_id: str) -> bool:
        """Deletes a link by its ROWID."""
        if not row_id:
            raise DataValidationError("row_id must be provided for delete")
        try:
            table = self.get_table()
            table.delete_row(row_id)
            return True
        except CatalystError as e:
            logger.error(f"Error deleting link {row_id}: {e}")
            raise RepositoryError(f"Failed to delete link: {e}")

    async def count_by_criminal(self, criminal_id: str) -> int:
        """Counts how many crimes are linked to a criminal."""
        try:
            query = (
                f"SELECT COUNT(ROWID) FROM {self.table_name} "
                f"WHERE criminal_id = {self._zcql_escape(criminal_id)}"
            )
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                first_row = result[0]
                for table_data in first_row.values():
                    for val in table_data.values():
                        if isinstance(val, (int, float, str)) and str(val).isdigit():
                            return int(val)
            return 0
        except CatalystError as e:
            logger.error(f"Error counting links for criminal {criminal_id}: {e}")
            raise RepositoryError(f"Failed to count criminal links: {e}")
