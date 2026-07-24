from typing import List, Dict, Any, Optional
from fastapi import Request

from app.repositories.alert_repo import AlertRepository
from app.repositories.crime_repo import CrimeRepository
from app.repositories.fir_repo import FIRRepository
from app.repositories.hotspot_repo import HotspotRepository
from app.repositories.district_repo import DistrictRepository
from app.repositories.police_station_repo import PoliceStationRepository
from app.core.logger import logger
from app.schemas.alert import AlertResponse, AlertSummary
from app.core.exceptions import DataValidationError


class AlertService:
    """Service layer for Alert entity."""
    
    def __init__(self, request: Request, repo: AlertRepository):
        self.request = request
        self.repo = repo
        self.crime_repo = CrimeRepository(request)
        self.fir_repo = FIRRepository(request)
        self.hotspot_repo = HotspotRepository(request)
        self.district_repo = DistrictRepository(request)
        self.station_repo = PoliceStationRepository(request)

    async def get_alerts(self, status_filter: Optional[str] = None, severity: Optional[str] = None, district_id: Optional[str] = None, station_id: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieves alerts with optional filters."""
        logger.info("Fetching Alerts")
        if status_filter:
            return await self.repo.find_by_status(status_filter, limit=limit, offset=offset, district_id=district_id, station_id=station_id)
        return await self.repo.find_active(limit=limit, offset=offset, district_id=district_id, station_id=station_id)

    async def get_active_alerts(self, limit: int = 100, offset: int = 0, district_id: Optional[str] = None, station_id: Optional[str] = None, severity: Optional[str] = None, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves active alerts."""
        logger.info("Fetching active Alerts")
        if status_filter:
            return await self.repo.find_by_status(status_filter, limit=limit, offset=offset, district_id=district_id, station_id=station_id)
        return await self.repo.find_active(limit=limit, offset=offset, district_id=district_id, station_id=station_id, severity=severity)

    async def get_summary(self) -> Dict[str, Any]:
        """Retrieves alert summary counts."""
        logger.info("Fetching alert summary")
        total = await self.repo.count()
        active = await self.repo.count_by_status("ACTIVE")
        acknowledged = await self.repo.count_by_status("ACKNOWLEDGED")
        resolved = await self.repo.count_by_status("RESOLVED")
        critical = await self.repo.count_by_severity("CRITICAL")
        return {
            "total_alerts": total,
            "active_alerts": active,
            "acknowledged_alerts": acknowledged,
            "resolved_alerts": resolved,
            "critical_alerts": critical,
        }

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an Alert by ID."""
        logger.info(f"Fetching Alert {id}")
        return await self.repo.find_by_id(id)

    async def acknowledge_alert(self, id: str) -> Dict[str, Any]:
        """Acknowledges an alert."""
        logger.info(f"Acknowledging Alert {id}")
        existing = await self.repo.find_by_id(id)
        if not existing:
            raise DataValidationError(f"Alert {id} not found")
        result = await self.repo.update(id, {"status": "ACKNOWLEDGED"})
        logger.info("Alert acknowledged")
        return result

    async def resolve_alert(self, id: str) -> Dict[str, Any]:
        """Resolves an alert."""
        logger.info(f"Resolving Alert {id}")
        existing = await self.repo.find_by_id(id)
        if not existing:
            raise DataValidationError(f"Alert {id} not found")
        result = await self.repo.update(id, {"status": "RESOLVED"})
        logger.info("Alert resolved")
        return result
