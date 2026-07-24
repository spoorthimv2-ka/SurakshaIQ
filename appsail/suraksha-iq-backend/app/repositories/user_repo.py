from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError, DataValidationError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger

class UserRepository(BaseCatalystRepository):
    """
    Repository for User entity backed by Catalyst Data Store.
    """
    def __init__(self, request: Request):
        super().__init__(request, table_name="User")

    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Retrieves a user by their email address."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE email = {self._zcql_escape(email)} LIMIT 1"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                return result[0].get(self.table_name)
            return None
        except CatalystError as e:
            logger.error(f"Error fetching user by email {email}: {e}")
            raise RepositoryError(f"Failed to fetch user by email: {e}")

    async def find_by_role(self, role: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieves users by their role."""
        try:
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE role = {self._zcql_escape(role)} "
                f"LIMIT {offset_val}, {int(limit)}"
            )
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching users by role {role}: {e}")
            raise RepositoryError(f"Failed to fetch users by role: {e}")

    async def find_active(self, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves active users with pagination."""
        try:
            self._validate_column(self.table_name, sort_by)
            if sort_order.upper() not in ("ASC", "DESC"):
                raise DataValidationError("sort_order must be ASC or DESC")
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE status = {self._zcql_escape('ACTIVE')} "
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
            logger.error(f"Error fetching active users: {e}")
            raise RepositoryError(f"Failed to fetch active users: {e}")

    async def find_by_id(self, row_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a user by ROWID."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE ROWID = {self._zcql_escape(row_id)} LIMIT 1"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                return result[0].get(self.table_name)
            return None
        except CatalystError as e:
            logger.error(f"Error fetching user {row_id}: {e}")
            raise RepositoryError(f"Failed to fetch user: {e}")

    async def count(self) -> int:
        """Counts all users."""
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
            logger.error(f"Error counting users: {e}")
            raise RepositoryError(f"Failed to count users: {e}")
