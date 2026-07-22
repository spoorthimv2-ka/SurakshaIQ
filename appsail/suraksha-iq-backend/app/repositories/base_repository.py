from typing import List, Dict, Any, Optional
from fastapi import Request
from zcatalyst_sdk.exceptions import CatalystError
from app.core.catalyst import catalyst_manager
from app.core.exceptions import RepositoryError, DataValidationError
from app.core.logger import logger


class BaseCatalystRepository:
    """
    Generic CRUD base repository backed by Catalyst Data Store.
    Expects a table_name to be defined by subclasses.
    """

    def __init__(self, request: Request, table_name: str):
        if not table_name:
            raise ValueError("table_name must be provided")
        if not isinstance(request, Request):
            raise ValueError("A FastAPI Request object is required for Catalyst initialization.")
        self.request = request
        self.table_name = table_name
        self._table = None

    @property
    def datastore(self):
        return catalyst_manager.get_datastore(self.request)

    @property
    def zcql(self):
        return catalyst_manager.get_zcql(self.request)

    def get_table(self):
        """Returns the Catalyst Table instance."""
        if self._table is None:
            self._table = self.datastore.table(self.table_name)
        return self._table

    async def create(self, row_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new record in the Catalyst Data Store."""
        if not row_data:
            raise DataValidationError("Row data cannot be empty")
        try:
            table = self.get_table()
            return table.insert_row(row_data)
        except CatalystError as e:
            logger.error(f"Error creating record in {self.table_name}: {e}")
            raise RepositoryError(f"Failed to create record: {e}")

    async def update(self, row_id: str, row_data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing record by its ROWID."""
        if not row_id:
            raise DataValidationError("row_id must be provided for update")
        if not row_data:
            raise DataValidationError("Row data cannot be empty")
        try:
            table = self.get_table()
            row_data['ROWID'] = row_id
            return table.update_row(row_data)
        except CatalystError as e:
            logger.error(f"Error updating record {row_id} in {self.table_name}: {e}")
            raise RepositoryError(f"Failed to update record: {e}")

    async def delete(self, row_id: str) -> bool:
        """Deletes a record by its ROWID."""
        if not row_id:
            raise DataValidationError("row_id must be provided for delete")
        try:
            table = self.get_table()
            table.delete_row(row_id)
            return True
        except CatalystError as e:
            logger.error(f"Error deleting record {row_id} from {self.table_name}: {e}")
            raise RepositoryError(f"Failed to delete record: {e}")

    async def find_by_id(self, row_id: str) -> Optional[Dict[str, Any]]:
        """Finds a single record by its ROWID."""
        if not row_id:
            raise DataValidationError("row_id must be provided for find_by_id")
        try:
            table = self.get_table()
            return table.get_row(row_id)
        except CatalystError as e:
            logger.warning(f"Record {row_id} not found in {self.table_name}: {e}")
            return None

    async def find_all(self, limit: int = 100, next_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves all records from the table."""
        try:
            query = f"SELECT * FROM {self.table_name} LIMIT {limit}"
            result = self.zcql.execute_query(query)
            return [item[self.table_name] for item in result if self.table_name in item]
        except CatalystError as e:
            logger.error(f"Error finding all records in {self.table_name}: {e}")
            raise RepositoryError(f"Failed to fetch records: {e}")

    async def exists(self, column: str, value: Any) -> bool:
        """Checks if a record exists matching the given column and value."""
        if not column or value is None:
            raise DataValidationError("Both column and value must be provided for exists check")
        try:
            formatted_value = f"'{value}'" if isinstance(value, str) else value
            query = f"SELECT ROWID FROM {self.table_name} WHERE {column} = {formatted_value} LIMIT 1"
            result = self.zcql.execute_query(query)
            return len(result) > 0
        except CatalystError as e:
            logger.error(f"Error checking existence in {self.table_name}: {e}")
            raise RepositoryError(f"Failed to check existence: {e}")

    async def count(self) -> int:
        """Returns the total number of records in the table."""
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
            logger.error(f"Error counting records in {self.table_name}: {e}")
            raise RepositoryError(f"Failed to count records: {e}")
