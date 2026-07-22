from typing import Any, Dict, List, Optional
from datetime import datetime, timezone, timedelta
from fastapi import Request
from app.repositories.hotspot_repo import HotspotRepository
from app.repositories.district_repo import DistrictRepository
from app.repositories.police_station_repo import PoliceStationRepository
from app.repositories.fir_repo import FIRRepository
from app.core.logger import logger
from app.schemas.hotspot import (
    HotspotResponse,
    DistrictHotspotResponse,
    StationHotspotResponse,
    HotspotSummaryResponse,
)


class HotspotService:
    """Service layer for hotspot analysis."""

    SEVERITY_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def __init__(self, request: Request):
        self.request = request
        self.repo = HotspotRepository(request)
        self.district_repo = DistrictRepository(request)
        self.station_repo = PoliceStationRepository(request)
        self.fir_repo = FIRRepository(request)

    async def get_hotspots(
        self,
        officer: Dict[str, Any],
        district_id: Optional[str] = None,
        station_id: Optional[str] = None,
        crime_type: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[HotspotResponse]:
        """Retrieves hotspot records with filters."""
        del officer
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=30)

        date_from = start_date.strftime("%Y-%m-%dT%H:%M:%SZ") if start_date else None
        date_to = end_date.strftime("%Y-%m-%dT%H:%M:%SZ") if end_date else None

        crimes = await self.repo.find_filtered(
            district_id=district_id,
            station_id=station_id,
            crime_type=crime_type,
            status=status,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
        )

        district_map: Dict[str, Dict[str, Any]] = {}
        for c in crimes:
            did = c.get("district_id", "UNKNOWN")
            sid = c.get("station_id", "UNKNOWN")
            key = f"{did}:{sid}"
            if key not in district_map:
                district_map[key] = {
                    "district_id": did,
                    "police_station": sid,
                    "crime_count": 0,
                    "latest_date": None,
                    "statuses": [],
                }
            entry = district_map[key]
            entry["crime_count"] += 1
            created = c.get("CREATEDTIME", "")
            if created and (entry["latest_date"] is None or created > entry["latest_date"]):
                entry["latest_date"] = created
            entry["statuses"].append(c.get("status", "ACTIVE"))

        results: List[HotspotResponse] = []
        for key, entry in district_map.items():
            score = self._compute_hotspot_score(entry["crime_count"], entry["latest_date"], entry["statuses"])
            severity = self._determine_severity(score)
            results.append(
                HotspotResponse(
                    id=key,
                    district=entry["district_id"],
                    police_station=entry["police_station"],
                    crime_count=entry["crime_count"],
                    hotspot_score=round(score, 2),
                    severity=severity,
                    latest_crime_date=entry["latest_date"],
                )
            )

        return sorted(results, key=lambda x: x.hotspot_score, reverse=True)

    async def get_district_hotspots(
        self,
        officer: Dict[str, Any],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[DistrictHotspotResponse]:
        """Retrieves hotspot summary per district."""
        del officer
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=30)

        date_from = start_date.strftime("%Y-%m-%dT%H:%M:%SZ") if start_date else None
        date_to = end_date.strftime("%Y-%m-%dT%H:%M:%SZ") if end_date else None

        districts = await self.district_repo.find_active(limit=1000)
        results: List[DistrictHotspotResponse] = []

        for d in districts:
            did = d.get("ROWID", d.get("id", ""))
            dname = d.get("name", did)
            crimes = await self.repo.count_by_district(did, date_from=date_from, date_to=date_to)
            firs = await self.fir_repo.count_by_status("ACTIVE")

            score = self._compute_hotspot_score(crimes, None, [])
            trend = self._compute_trend(crimes)

            results.append(
                DistrictHotspotResponse(
                    district_id=did,
                    district_name=dname,
                    total_crimes=crimes,
                    hotspot_score=round(score, 2),
                    active_firs=firs,
                    trend=trend,
                )
            )

        return sorted(results, key=lambda x: x.hotspot_score, reverse=True)

    async def get_station_hotspots(
        self,
        officer: Dict[str, Any],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[StationHotspotResponse]:
        """Retrieves hotspot summary per police station."""
        del officer
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=30)

        date_from = start_date.strftime("%Y-%m-%dT%H:%M:%SZ") if start_date else None
        date_to = end_date.strftime("%Y-%m-%dT%H:%M:%SZ") if end_date else None

        stations = await self.station_repo.find_active(limit=1000)
        results: List[StationHotspotResponse] = []

        for s in stations:
            sid = s.get("ROWID", s.get("id", ""))
            sname = s.get("name", sid)
            did = s.get("district_id", "UNKNOWN")
            dname = s.get("district_name", did)
            crimes = await self.repo.count_by_station(sid, date_from=date_from, date_to=date_to)
            firs = await self.fir_repo.count_by_status("ACTIVE")

            score = self._compute_hotspot_score(crimes, None, [])
            results.append(
                StationHotspotResponse(
                    station_id=sid,
                    station_name=sname,
                    district_id=did,
                    district_name=dname,
                    crime_count=crimes,
                    hotspot_score=round(score, 2),
                    active_firs=firs,
                )
            )

        return sorted(results, key=lambda x: x.hotspot_score, reverse=True)

    async def get_top_hotspots(
        self,
        officer: Dict[str, Any],
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[HotspotResponse]:
        """Returns the top-ranked hotspots."""
        return await self.get_hotspots(
            officer,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

    async def get_summary(
        self,
        officer: Dict[str, Any],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> HotspotSummaryResponse:
        """Returns aggregated hotspot summary counts."""
        hotspots = await self.get_hotspots(officer, start_date=start_date, end_date=end_date, limit=1000)
        high = sum(1 for h in hotspots if h.severity == "HIGH")
        medium = sum(1 for h in hotspots if h.severity == "MEDIUM")
        low = sum(1 for h in hotspots if h.severity == "LOW")
        return HotspotSummaryResponse(
            total_hotspots=len(hotspots),
            high_severity_count=high,
            medium_severity_count=medium,
            low_severity_count=low,
        )

    def _compute_hotspot_score(self, crime_count: int, latest_date: Optional[str], statuses: List[str]) -> float:
        """Computes a deterministic hotspot score."""
        frequency_score = crime_count * 10.0

        recency_score = 0.0
        if latest_date:
            try:
                dt = datetime.strptime(latest_date[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                days_ago = (datetime.now(timezone.utc) - dt).days
                if days_ago <= 7:
                    recency_score = 30.0
                elif days_ago <= 30:
                    recency_score = 20.0
                elif days_ago <= 90:
                    recency_score = 10.0
            except (ValueError, TypeError):
                recency_score = 0.0

        severity_score = 0.0
        active_count = sum(1 for s in statuses if s == "ACTIVE")
        if active_count:
            severity_score = min(active_count * 5.0, 40.0)

        return frequency_score + recency_score + severity_score

    def _determine_severity(self, score: float) -> str:
        """Determines severity label from hotspot score."""
        if score >= 100.0:
            return "HIGH"
        if score >= 50.0:
            return "MEDIUM"
        return "LOW"

    def _compute_trend(self, count: int) -> str:
        """Computes a simple trend string based on count."""
        if count >= 10:
            return "rising"
        if count >= 5:
            return "stable"
        return "declining"
