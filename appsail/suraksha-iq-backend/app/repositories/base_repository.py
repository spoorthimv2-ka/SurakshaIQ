from typing import List, Dict, Any, Optional, Tuple
from fastapi import Request
from zcatalyst_sdk.exceptions import CatalystError
from app.core.catalyst import catalyst_manager
from app.core.exceptions import RepositoryError, DataValidationError
from app.core.logger import logger


ALLOWED_COLUMNS: Dict[str, Tuple[str, ...]] = {
    "Crime": (
        "ROWID", "fir_number", "crime_type", "description",
        "incident_date", "status", "latitude", "longitude", "address",
        "district_id", "station_id", "CREATEDTIME", "MODIFIEDTIME",
        "title", "location", "victim_name", "suspect_name", "alias",
        "vehicle_number", "mobile_number", "weapon", "modus_operandi",
        "keywords", "ipc_sections", "severity",
    ),
    "Criminal": (
        "ROWID", "name", "alias", "age", "gender",
        "last_known_location", "risk_level", "status", "photo_url",
        "CREATEDTIME", "MODIFIEDTIME",
    ),
    "FIR": (
        "ROWID", "fir_number", "crime_id", "district_id", "station_id",
        "officer_id", "status", "fir_date", "sections", "summary",
        "CREATEDTIME", "MODIFIEDTIME",
        "victim_name", "suspect_name", "vehicle_number", "mobile_number",
        "ipc_sections", "description",
    ),
    "District": (
        "ROWID", "name", "state", "region_code",
        "latitude", "longitude", "status", "code",
        "CREATEDTIME", "MODIFIEDTIME",
    ),
    "PoliceStation": (
        "ROWID", "name", "station_code", "address",
        "district_id", "latitude", "longitude", "status",
        "CREATEDTIME", "MODIFIEDTIME",
    ),
    "Officer": (
        "ROWID", "catalyst_user_id", "name", "email", "role", "rank",
        "designation", "hashed_password", "police_station_id", "status",
        "CREATEDTIME", "MODIFIEDTIME",
    ),
    "Alert": (
        "ROWID", "type", "severity", "status", "message",
        "district_id", "created_at", "resolved_at", "title", "description",
        "source", "entity_id", "entity_type", "station_id", "recommended_action",
        "CREATEDTIME", "MODIFIEDTIME",
    ),
    "Report": (
        "ROWID", "name", "report_type", "parameters_json",
        "created_by_officer_id", "created_at",
    ),
    "CrimeCriminalLink": (
        "ROWID", "crime_id", "criminal_id", "role",
        "linked_by_officer_id", "linked_at", "notes",
        "CREATEDTIME", "MODIFIEDTIME",
    ),
    "User": (
        "ROWID", "name", "email", "role", "status",
        "CREATEDTIME", "MODIFIEDTIME",
    ),
    "AuditLog": (
        "ROWID", "action", "user", "target", "metadata", "created_at",
    ),
    "Search": (),
    "CrimeHotspotCluster": (
        "ROWID", "cluster_id", "district_id", "station_id",
        "center_lat", "center_lon", "radius_m", "crime_count",
        "period_start", "period_end", "scored_at",
    ),
    "PredictionLedger": (
        "ROWID", "entity_type", "entity_id", "entity_name",
        "prediction_type", "score", "level", "factors",
        "model_version", "scored_at", "CREATEDTIME",
    ),
    "NetworkNode": (
        "ROWID", "label", "node_type", "entity_type", "entity_id",
        "district_id", "risk_score", "status", "CREATEDTIME", "MODIFIEDTIME",
    ),
    "Anomaly": (
        "ROWID", "anomaly_type", "affected_entity_name", "severity",
        "district_id", "status", "description", "CREATEDTIME", "MODIFIEDTIME",
    ),
    "PredictiveRisk": (
        "ROWID", "entity_name", "entity_type", "risk_score", "risk_level",
        "district_id", "status", "factors_json", "CREATEDTIME", "MODIFIEDTIME",
    ),
}


class BaseCatalystRepository:
    """
    Generic CRUD base repository backed by Catalyst Data Store.
    Expects a table_name to be defined by subclasses.
    """

    def __init__(self, request: Request, table_name: str):
        if not table_name:
            raise ValueError("table_name must be provided")
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

    @staticmethod
    def _zcql_like(value: str) -> str:
        s = str(value)
        s = s.replace("\\", "\\\\")
        s = s.replace("%", "\\%")
        s = s.replace("_", "\\_")
        s = s.replace("'", "''")
        return f"'%{s}%'"

    @staticmethod
    def _validate_column(table_name: str, column: str) -> None:
        allowed = ALLOWED_COLUMNS.get(table_name, ())
        if column not in allowed:
            raise DataValidationError(
                f"Column '{column}' is not allowed for table '{table_name}'"
            )

    @staticmethod
    def _zcql_escape(value: Any) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        if isinstance(value, (int, float)):
            return str(value)
        s = str(value).replace("'", "''")
        return f"'{s}'"

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
            query = f"SELECT * FROM {self.table_name} LIMIT {int(limit)}"
            result = self.zcql.execute_query(query)
            return [item[self.table_name] for item in result if self.table_name in item]
        except CatalystError as e:
            logger.error(f"Error finding all records in {self.table_name}: {e}")
            raise RepositoryError(f"Failed to fetch records: {e}")

    async def exists(self, column: str, value: Any) -> bool:
        """Checks if a record exists matching the given column and value."""
        if not column or value is None:
            raise DataValidationError("Both column and value must be provided for exists check")
        self._validate_column(self.table_name, column)
        try:
            query = f"SELECT ROWID FROM {self.table_name} WHERE {column} = {self._zcql_escape(value)} LIMIT 1"
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
