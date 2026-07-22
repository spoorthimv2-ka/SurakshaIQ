from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.repositories.crime_repo import CrimeRepository
from app.repositories.fir_repo import FIRRepository
from app.repositories.hotspot_repo import HotspotRepository
from app.repositories.repeat_offender_repo import RepeatOffenderRepository
from app.repositories.network_repo import NetworkRepository
from app.repositories.predictive_risk_repo import PredictiveRiskRepository
from app.repositories.anomaly_repo import AnomalyRepository
from app.repositories.alert_repo import AlertRepository
from app.repositories.report_repo import ReportRepository
from app.repositories.district_repo import DistrictRepository
from app.repositories.police_station_repo import PoliceStationRepository
from app.core.exceptions import RepositoryError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger

class SearchRepository(BaseCatalystRepository):
    """
    Repository for global search aggregations backed by Catalyst Data Store.
    Reuses existing repositories for data retrieval.
    """

    def __init__(self, request: Request):
        super().__init__(request, table_name="Search")
        self.crime_repo = CrimeRepository(request)
        self.fir_repo = FIRRepository(request)
        self.hotspot_repo = HotspotRepository(request)
        self.repeat_offender_repo = RepeatOffenderRepository(request)
        self.network_repo = NetworkRepository(request)
        self.predictive_risk_repo = PredictiveRiskRepository(request)
        self.anomaly_repo = AnomalyRepository(request)
        self.alert_repo = AlertRepository(request)
        self.report_repo = ReportRepository(request)
        self.district_repo = DistrictRepository(request)
        self.station_repo = PoliceStationRepository(request)

    async def search_crimes(self, keyword: str, district_id: Optional[str] = None, station_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Searches crimes by keyword with optional filters."""
        try:
            results = await self.crime_repo.find_all_with_filters(
                limit=limit,
                keyword=keyword,
                district_id=district_id,
                station_id=station_id,
            )
            for r in results:
                r["_category"] = "Crime"
            return results
        except CatalystError as e:
            logger.error(f"Error searching crimes: {e}")
            raise RepositoryError(f"Failed to search crimes: {e}")

    async def search_firs(self, keyword: str, district_id: Optional[str] = None, station_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Searches FIRs by keyword with optional filters."""
        try:
            results = await self.fir_repo.find_all_with_filters(
                limit=limit,
                district_id=district_id,
                station_id=station_id,
            )
            for r in results:
                r["_category"] = "FIR"
            return results
        except CatalystError as e:
            logger.error(f"Error searching FIRs: {e}")
            raise RepositoryError(f"Failed to search FIRs: {e}")

    async def search_hotspots(self, keyword: str, district_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Searches hotspots by keyword."""
        try:
            results = await self.hotspot_repo.find_filtered(district_id=district_id, limit=limit)
            if keyword:
                filtered = []
                for h in results:
                    if keyword.lower() in h.get("district", "").lower() or keyword.lower() in h.get("police_station", "").lower():
                        h["_category"] = "Hotspot"
                        filtered.append(h)
                return filtered
            for r in results:
                r["_category"] = "Hotspot"
            return results
        except CatalystError as e:
            logger.error(f"Error searching hotspots: {e}")
            raise RepositoryError(f"Failed to search hotspots: {e}")

    async def search_repeat_offenders(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Searches repeat offenders by keyword."""
        try:
            results = await self.repeat_offender_repo.search(search_term=keyword, limit=limit)
            for r in results:
                r["_category"] = "RepeatOffender"
            return results
        except CatalystError as e:
            logger.error(f"Error searching repeat offenders: {e}")
            raise RepositoryError(f"Failed to search repeat offenders: {e}")

    async def search_network_nodes(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Searches network nodes by keyword."""
        try:
            nodes = await self.network_repo.find_all_nodes(limit=limit)
            if keyword:
                filtered = []
                for n in nodes:
                    if keyword.lower() in n.get("label", "").lower() or keyword.lower() in n.get("node_type", "").lower():
                        n["_category"] = "Network"
                        filtered.append(n)
                return filtered
            for r in nodes:
                r["_category"] = "Network"
            return nodes
        except CatalystError as e:
            logger.error(f"Error searching network nodes: {e}")
            raise RepositoryError(f"Failed to search network nodes: {e}")

    async def search_risk_predictions(self, keyword: str, district_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Searches risk predictions by keyword."""
        try:
            risks = await self.predictive_risk_repo.find_all(limit=limit)
            filtered = []
            for r in risks:
                if keyword.lower() in r.get("entity_name", "").lower() or keyword.lower() in r.get("entity_type", "").lower():
                    if district_id and r.get("district_id") != district_id:
                        continue
                    r["_category"] = "PredictiveRisk"
                    filtered.append(r)
            return filtered
        except CatalystError as e:
            logger.error(f"Error searching risk predictions: {e}")
            raise RepositoryError(f"Failed to search risk predictions: {e}")

    async def search_anomalies(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Searches anomalies by keyword."""
        try:
            anomalies = await self.anomaly_repo.find_all(limit=limit)
            filtered = []
            for a in anomalies:
                if keyword.lower() in a.get("anomaly_type", "").lower() or keyword.lower() in a.get("affected_entity_name", "").lower():
                    a["_category"] = "Anomaly"
                    filtered.append(a)
            return filtered
        except CatalystError as e:
            logger.error(f"Error searching anomalies: {e}")
            raise RepositoryError(f"Failed to search anomalies: {e}")

    async def search_alerts(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Searches alerts by keyword."""
        try:
            alerts = await self.alert_repo.find_all(limit=limit)
            filtered = []
            for a in alerts:
                if keyword.lower() in a.get("title", "").lower() or keyword.lower() in a.get("description", "").lower():
                    a["_category"] = "Alert"
                    filtered.append(a)
            return filtered
        except CatalystError as e:
            logger.error(f"Error searching alerts: {e}")
            raise RepositoryError(f"Failed to search alerts: {e}")

    async def search_reports(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Searches reports by keyword."""
        try:
            results = await self.report_repo.search(search_term=keyword, limit=limit)
            for r in results:
                r["_category"] = "Report"
            return results
        except CatalystError as e:
            logger.error(f"Error searching reports: {e}")
            raise RepositoryError(f"Failed to search reports: {e}")

    async def get_districts(self) -> List[Dict[str, Any]]:
        """Retrieves all districts for filters."""
        try:
            return await self.district_repo.find_active(limit=1000)
        except CatalystError as e:
            logger.error(f"Error fetching districts: {e}")
            raise RepositoryError(f"Failed to fetch districts: {e}")

    async def get_stations(self, district_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves all police stations for filters."""
        try:
            if district_id:
                return await self.station_repo.find_by_district(district_id, limit=1000)
            return await self.station_repo.find_active(limit=1000)
        except CatalystError as e:
            logger.error(f"Error fetching stations: {e}")
            raise RepositoryError(f"Failed to fetch stations: {e}")
