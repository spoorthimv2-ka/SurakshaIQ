from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.repositories.alert_repo import AlertRepository
from app.repositories.crime_repo import CrimeRepository
from app.repositories.fir_repo import FIRRepository
from app.repositories.hotspot_repo import HotspotRepository
from app.repositories.district_repo import DistrictRepository
from app.repositories.police_station_repo import PoliceStationRepository
from app.core.logger import logger
from app.schemas.alert import AlertResponse, AlertSummary, AlertStatistics, AlertCreate, AlertUpdate
from app.core.exceptions import DataValidationError, RepositoryError


class AlertService:
    """Service layer for Alert entity."""
    
    def __init__(self, repo: AlertRepository):
        self.repo = repo
        self.crime_repo = CrimeRepository()
        self.fir_repo = FIRRepository()
        self.hotspot_repo = HotspotRepository()
        self.district_repo = DistrictRepository()
        self.station_repo = PoliceStationRepository()

    async def get_alerts(self, status_filter: Optional[str] = None, severity: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieves alerts with optional filters."""
        logger.info("Fetching Alerts")
        if status_filter:
            return await self.repo.find_by_status(status_filter, limit=limit, offset=offset)
        return await self.repo.find_active(limit=limit, offset=offset)

    async def get_active_alerts(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieves active alerts."""
        logger.info("Fetching active Alerts")
        return await self.repo.find_active(limit=limit, offset=offset)

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

    async def get_statistics(self) -> Dict[str, Any]:
        """Retrieves alert statistics."""
        logger.info("Fetching alert statistics")
        alerts = await self.repo.find_all(limit=1000)

        by_severity: Dict[str, int] = {}
        by_source: Dict[str, int] = {}
        by_district: Dict[str, int] = {}

        for alert in alerts:
            severity = alert.get("severity", "UNKNOWN")
            source = alert.get("source", "UNKNOWN")
            district = alert.get("district_id", "UNKNOWN")

            by_severity[severity] = by_severity.get(severity, 0) + 1
            by_source[source] = by_source.get(source, 0) + 1
            if district:
                by_district[district] = by_district.get(district, 0) + 1

        return {
            "by_severity": [{"severity": k, "count": v} for k, v in by_severity.items()],
            "by_source": [{"source": k, "count": v} for k, v in by_source.items()],
            "by_district": [{"district_id": k, "count": v} for k, v in by_district.items()],
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

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new Alert."""
        logger.info("Creating Alert")
        if not data.get("title"):
            raise DataValidationError("Title is required")
        if not data.get("description"):
            raise DataValidationError("Description is required")
        if not data.get("severity"):
            raise DataValidationError("Severity is required")
        if not data.get("source"):
            raise DataValidationError("Source is required")
        result = await self.repo.create(data)
        logger.info("Alert Created")
        return result

    async def generate_alerts(self) -> List[Dict[str, Any]]:
        """Generates alerts from existing data sources."""
        logger.info("Generating alerts from existing data")
        alerts: List[Dict[str, Any]] = []

        crime_alerts = await self._generate_crime_alerts()
        alerts.extend(crime_alerts)

        fir_alerts = await self._generate_fir_alerts()
        alerts.extend(fir_alerts)

        hotspot_alerts = await self._generate_hotspot_alerts()
        alerts.extend(hotspot_alerts)

        return alerts

    async def _generate_crime_alerts(self) -> List[Dict[str, Any]]:
        """Generates crime-related alerts."""
        alerts = []
        districts = await self.district_repo.find_active(limit=1000)
        for district in districts:
            did = district.get("ROWID", "")
            dname = district.get("name", did)
            crimes = await self.crime_repo.find_by_district(did, limit=100)
            if len(crimes) >= 20:
                alerts.append({
                    "title": f"Critical crime spike in {dname}",
                    "description": f"{len(crimes)} crimes detected in district {dname}",
                    "severity": "CRITICAL",
                    "source": "CRIME_ANALYSIS",
                    "entity_id": did,
                    "entity_type": "District",
                    "district_id": did,
                    "station_id": None,
                    "recommended_action": "Deploy additional patrols and investigative resources",
                    "status": "ACTIVE",
                })
            elif len(crimes) >= 10:
                alerts.append({
                    "title": f"High crime volume in {dname}",
                    "description": f"{len(crimes)} crimes detected in district {dname}",
                    "severity": "HIGH",
                    "source": "CRIME_ANALYSIS",
                    "entity_id": did,
                    "entity_type": "District",
                    "district_id": did,
                    "station_id": None,
                    "recommended_action": "Increase patrol frequency and review resource allocation",
                    "status": "ACTIVE",
                })
        return alerts

    async def _generate_fir_alerts(self) -> List[Dict[str, Any]]:
        """Generates FIR-related alerts."""
        alerts = []
        stations = await self.station_repo.find_active(limit=1000)
        for station in stations:
            sid = station.get("ROWID", "")
            sname = station.get("name", sid)
            did = station.get("district_id", "")
            firs = await self.fir_repo.find_by_station(sid, limit=100)
            active_firs = [f for f in firs if f.get("status") == "ACTIVE"]
            if len(active_firs) >= 10:
                alerts.append({
                    "title": f"FIR backlog at {sname}",
                    "description": f"{len(active_firs)} active FIRs pending investigation at {sname}",
                    "severity": "HIGH",
                    "source": "FIR_ANALYSIS",
                    "entity_id": sid,
                    "entity_type": "PoliceStation",
                    "district_id": did,
                    "station_id": sid,
                    "recommended_action": "Reassign officers and expedite pending investigations",
                    "status": "ACTIVE",
                })
        return alerts

    async def _generate_hotspot_alerts(self) -> List[Dict[str, Any]]:
        """Generates hotspot-related alerts."""
        alerts = []
        districts = await self.district_repo.find_active(limit=1000)
        for district in districts:
            did = district.get("ROWID", "")
            dname = district.get("name", did)
            crime_count = await self.hotspot_repo.count_by_district(did)
            if crime_count >= 15:
                alerts.append({
                    "title": f"Hotspot alert: {dname}",
                    "description": f"Elevated crime concentration detected in {dname} with {crime_count} incidents",
                    "severity": "CRITICAL",
                    "source": "HOTSPOT_ANALYSIS",
                    "entity_id": did,
                    "entity_type": "District",
                    "district_id": did,
                    "station_id": None,
                    "recommended_action": "Increase surveillance and targeted patrols in hotspot area",
                    "status": "ACTIVE",
                })
        return alerts
