from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError, DataValidationError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger


class PredictionLedgerRepository(BaseCatalystRepository):
    """
    Repository for immutable prediction history backed by Catalyst Data Store.
    Table: PredictionLedger
    """

    def __init__(self, request: Request):
        super().__init__(request, table_name="PredictionLedger")

    async def record(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Records a single prediction run."""
        if not row:
            raise DataValidationError("Ledger row cannot be empty")
        try:
            table = self.get_table()
            return table.insert_row(row)
        except CatalystError as e:
            logger.error(f"Error recording prediction ledger entry: {e}")
            raise RepositoryError(f"Failed to record ledger entry: {e}")

    async def history_for_entity(
        self,
        entity_type: str,
        entity_id: str,
        prediction_type: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Retrieves historical scores for a specific entity."""
        try:
            self._validate_column(self.table_name, "entity_type")
            self._validate_column(self.table_name, "entity_id")
            self._validate_column(self.table_name, "prediction_type")
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE entity_type = {self._zcql_escape(entity_type)} "
                f"AND entity_id = {self._zcql_escape(entity_id)} "
                f"AND prediction_type = {self._zcql_escape(prediction_type)} "
                f"ORDER BY scored_at DESC LIMIT {int(limit)}"
            )
            result = self.zcql.execute_query(query)
            return [item[self.table_name] for item in result if self.table_name in item]
        except CatalystError as e:
            logger.error(f"Error fetching ledger history: {e}")
            raise RepositoryError(f"Failed to fetch ledger history: {e}")

    async def history_by_type(
        self,
        prediction_type: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Retrieves recent ledger entries for a prediction type."""
        try:
            self._validate_column(self.table_name, "prediction_type")
            offset_val = max(int(offset), 0)
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE prediction_type = {self._zcql_escape(prediction_type)} "
                f"ORDER BY scored_at DESC LIMIT {offset_val}, {int(limit)}"
            )
            result = self.zcql.execute_query(query)
            return [item[self.table_name] for item in result if self.table_name in item]
        except CatalystError as e:
            logger.error(f"Error fetching ledger by type: {e}")
            raise RepositoryError(f"Failed to fetch ledger by type: {e}")
