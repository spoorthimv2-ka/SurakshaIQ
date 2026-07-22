from typing import Optional, Dict, Any
from zcatalyst_sdk.exceptions import CatalystError
from app.core.catalyst import catalyst_manager
from app.core.exceptions import RepositoryError
from app.core.logger import logger


class CatalystOfficerRepository:
    """Authentication repository backed by Zoho Catalyst Data Store."""

    def __init__(self):
        self.table_name = "Officer"
        self.datastore = catalyst_manager.get_datastore()
        self.zcql = catalyst_manager.get_zcql()
        self.table = self.datastore.table(self.table_name)

    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Retrieves an officer by email using ZCQL."""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE email = '{email}' LIMIT 1"
            result = self.zcql.execute_query(query)
            if result and len(result) > 0:
                return result[0].get(self.table_name)
            return None
        except CatalystError as e:
            logger.error(f"Error fetching officer by email {email}: {e}")
            raise RepositoryError(f"Failed to fetch officer by email: {e}")

    async def find_by_id(self, officer_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an officer by ROWID."""
        try:
            row = self.table.get_row(officer_id)
            if row:
                return row
            return None
        except CatalystError as e:
            logger.warning(f"Officer {officer_id} not found in {self.table_name}: {e}")
            return None

    async def create_with_password(self, data: Dict[str, Any], hashed_password: str) -> Dict[str, Any]:
        """Creates a new officer record with hashed password."""
        try:
            row_data = dict(data)
            row_data["hashed_password"] = hashed_password
            return self.table.insert_row(row_data)
        except CatalystError as e:
            logger.error(f"Error creating officer in {self.table_name}: {e}")
            raise RepositoryError(f"Failed to create officer: {e}")

    async def update_password(self, officer_id: str, hashed_password: str) -> Optional[Dict[str, Any]]:
        """Updates the hashed password for an officer."""
        try:
            row_data = {"hashed_password": hashed_password}
            row_data["ROWID"] = officer_id
            return self.table.update_row(row_data)
        except CatalystError as e:
            logger.error(f"Error updating password for officer {officer_id}: {e}")
            raise RepositoryError(f"Failed to update officer password: {e}")
