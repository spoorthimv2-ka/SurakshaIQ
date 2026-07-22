from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import Request
from app.repositories.fir_repo import FIRRepository
from app.repositories.district_repo import DistrictRepository
from app.repositories.police_station_repo import PoliceStationRepository
from app.repositories.officer_repo import OfficerRepository
from app.schemas.enums import EntityStatus
from app.core.logger import logger
from app.core.exceptions import DataValidationError

class FIRService:
    """Service layer for FIR entity."""
    
    def __init__(self, request: Request, repo: FIRRepository):
        self.request = request
        self.repo = repo
        self.district_repo = DistrictRepository(request)
        self.station_repo = PoliceStationRepository(request)
        self.officer_repo = OfficerRepository(request)

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new FIR."""
        logger.info("Creating FIR")
        
        self.validate_fir_data(data)
        
        district = await self.district_repo.find_by_id(data.get("district_id", ""))
        if not district:
            raise DataValidationError(f"District {data['district_id']} does not exist")
        
        station = await self.station_repo.find_by_id(data.get("station_id", ""))
        if not station:
            raise DataValidationError(f"Police station {data['station_id']} does not exist")
        
        officer = await self.officer_repo.find_by_id(data.get("officer_id", ""))
        if not officer:
            raise DataValidationError(f"Officer {data['officer_id']} does not exist")
        
        if await self.repo.find_by_number(data.get("fir_number", "")):
            raise DataValidationError(f"FIR number {data['fir_number']} already exists")
        
        result = await self.repo.create(data)
        logger.info("FIR Created")
        return result

    async def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing FIR."""
        logger.info(f"Updating FIR {id}")
        
        existing = await self.repo.find_by_id(id)
        if not existing:
            raise DataValidationError(f"FIR {id} not found")
        
        merged = {**existing, **data}
        self.validate_fir_data(merged)
        
        if "fir_number" in merged:
            existing_number = await self.repo.find_by_number(merged["fir_number"])
            if existing_number and existing_number.get("ROWID") != id:
                raise DataValidationError(f"FIR number {merged['fir_number']} already exists")
        
        result = await self.repo.update(id, data)
        logger.info("FIR Updated")
        return result

    async def delete(self, id: str) -> bool:
        """Deletes an FIR."""
        logger.info(f"Deleting FIR {id}")
        result = await self.repo.delete(id)
        logger.info("FIR Deleted")
        return result

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an FIR by ID."""
        logger.info(f"Fetching FIR {id}")
        return await self.repo.find_by_id(id)

    async def get_all(self, limit: int = 100, next_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves all FIRs."""
        logger.info("Fetching all FIRs")
        return await self.repo.find_all(limit, next_token)

    async def find_all_with_filters(
        self,
        limit: int = 100,
        offset: int = 0,
        fir_number: Optional[str] = None,
        district_id: Optional[str] = None,
        station_id: Optional[str] = None,
        officer_id: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        sort_by: str = "CREATEDTIME",
        sort_order: str = "DESC",
    ) -> List[Dict[str, Any]]:
        """Retrieves FIRs with optional filters."""
        logger.info("Fetching filtered FIRs")
        self.validate_date_range(date_from, date_to)
        return await self.repo.find_all_with_filters(
            limit=limit,
            offset=offset,
            fir_number=fir_number,
            district_id=district_id,
            station_id=station_id,
            officer_id=officer_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def exists(self, column: str, value: Any) -> bool:
        """Checks if an FIR exists."""
        logger.info(f"Checking if FIR exists where {column}={value}")
        return await self.repo.exists(column, value)

    async def count(self) -> int:
        """Counts all FIRs."""
        logger.info("Counting all FIRs")
        return await self.repo.count()

    async def find_by_number(self, fir_number: str) -> Optional[Dict[str, Any]]:
        """Retrieves an FIR by its unique FIR number."""
        logger.info(f"Fetching FIR by number {fir_number}")
        return await self.repo.find_by_number(fir_number)

    async def find_by_station(self, station_id: str, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves FIRs scoped to a specific police station."""
        logger.info(f"Fetching FIRs for station {station_id}")
        return await self.repo.find_by_station(station_id, limit, offset, sort_by, sort_order)

    async def search(self, search_term: str, station_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs a text search on FIR number or description."""
        logger.info(f"Searching FIRs with term: {search_term}")
        return await self.repo.search(search_term, station_id, limit)

    def validate_fir_data(self, data: Dict[str, Any]) -> None:
        """Validates FIR data before creation or update."""
        required_fields = ["fir_number", "crime_id", "station_id", "officer_id", "description"]
        for field in required_fields:
            if not data.get(field):
                raise DataValidationError(f"Missing required field: {field}")
        
        status_value = data.get("status")
        if status_value:
            try:
                EntityStatus(status_value)
            except ValueError:
                raise DataValidationError(f"Invalid status: {status_value}")

    def validate_date_range(self, date_from: Optional[str], date_to: Optional[str]) -> None:
        """Validates date range filters."""
        if date_from:
            try:
                datetime.fromisoformat(date_from)
            except (ValueError, TypeError):
                raise DataValidationError(f"Invalid date_from format: {date_from}")
        if date_to:
            try:
                datetime.fromisoformat(date_to)
            except (ValueError, TypeError):
                raise DataValidationError(f"Invalid date_to format: {date_to}")
        if date_from and date_to and date_from > date_to:
            raise DataValidationError("date_from must be earlier than or equal to date_to")
