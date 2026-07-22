from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import Request
from app.repositories.crime_repo import CrimeRepository
from app.repositories.district_repo import DistrictRepository
from app.repositories.police_station_repo import PoliceStationRepository
from app.schemas.enums import EntityStatus
from app.core.exceptions import DataValidationError

class CrimeService:
    """Service layer for Crime entity."""
    
    def __init__(self, request: Request, repo: CrimeRepository):
        self.request = request
        self.repo = repo
        self.district_repo = DistrictRepository(request)
        self.station_repo = PoliceStationRepository(request)

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new Crime."""
        self.validate_crime_data(data)
        district = await self.district_repo.find_by_id(data.get("district_id", ""))
        if not district:
            raise DataValidationError(f"District {data['district_id']} does not exist")
        station = await self.station_repo.find_by_id(data.get("station_id", ""))
        if not station:
            raise DataValidationError(f"Police station {data['station_id']} does not exist")
        if await self.repo.check_duplicate(data["title"], data["district_id"], data["station_id"]):
            raise DataValidationError("Duplicate crime: a crime with the same title, district, and station already exists")
        return await self.repo.create(data)

    async def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing Crime."""
        existing = await self.repo.find_by_id(id)
        if not existing:
            raise DataValidationError(f"Crime {id} not found")
        merged = {**existing, **data}
        self.validate_crime_data(merged)
        if await self.repo.check_duplicate(merged["title"], merged["district_id"], merged["station_id"], exclude_id=id):
            raise DataValidationError("Duplicate crime: a crime with the same title, district, and station already exists")
        return await self.repo.update(id, data)

    async def delete(self, id: str) -> bool:
        """Deletes a Crime."""
        return await self.repo.delete(id)

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a Crime by ID."""
        return await self.repo.find_by_id(id)

    async def get_all(self, limit: int = 100, next_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves all Crimes."""
        return await self.repo.find_all(limit, next_token)

    async def find_all_with_filters(
        self,
        limit: int = 100,
        offset: int = 0,
        keyword: Optional[str] = None,
        district_id: Optional[str] = None,
        station_id: Optional[str] = None,
        crime_type: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        sort_by: str = "CREATEDTIME",
        sort_order: str = "DESC",
    ) -> List[Dict[str, Any]]:
        """Retrieves crimes with optional filters."""
        self.validate_date_range(date_from, date_to)
        return await self.repo.find_all_with_filters(
            limit=limit, offset=offset, keyword=keyword, district_id=district_id, station_id=station_id,
            crime_type=crime_type, status=status, date_from=date_from, date_to=date_to,
            sort_by=sort_by, sort_order=sort_order,
        )

    async def exists(self, column: str, value: Any) -> bool:
        """Checks if a Crime exists."""
        return await self.repo.exists(column, value)

    async def count(self) -> int:
        """Counts all Crimes."""
        return await self.repo.count()

    async def find_by_district(self, district_id: str, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves crimes scoped to a specific district."""
        return await self.repo.find_by_district(district_id, limit, offset, sort_by, sort_order)

    async def find_by_station(self, station_id: str, limit: int = 100, offset: int = 0, sort_by: str = "CREATEDTIME", sort_order: str = "DESC") -> List[Dict[str, Any]]:
        """Retrieves crimes scoped to a specific police station."""
        return await self.repo.find_by_station(station_id, limit, offset, sort_by, sort_order)

    async def search(self, search_term: str, district_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Performs a text search on crime title, description, or type."""
        return await self.repo.search(search_term, district_id, limit)

    def validate_crime_data(self, data: Dict[str, Any]) -> None:
        """Validates crime data before creation or update."""
        required_fields = ["title", "crime_type", "location", "district_id", "station_id"]
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
