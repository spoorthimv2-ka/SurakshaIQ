from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import Request

from app.repositories.crime_repo import CrimeRepository
from app.repositories.fir_repo import FIRRepository
from app.repositories.alert_repo import AlertRepository
from app.repositories.district_repo import DistrictRepository
from app.repositories.police_station_repo import PoliceStationRepository
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    RecentCrimeResponse,
    RecentFirResponse,
    CrimeTrendResponse,
    DistrictSummaryResponse,
)


class DashboardService:
    """
    Service layer for dashboard KPIs and statistics.
    Replaces the old SQLAlchemy-based DashboardRepository with Catalyst Data Store queries.
    """

    def __init__(self, request: Request):
        self.request = request
        self.crime_repo = CrimeRepository(request)
        self.fir_repo = FIRRepository(request)
        self.alert_repo = AlertRepository(request)
        self.district_repo = DistrictRepository(request)
        self.police_station_repo = PoliceStationRepository(request)

    async def get_summary(self, officer: Dict[str, Any]) -> DashboardSummaryResponse:
        """Returns high-level dashboard summary counts."""
        total_crimes = await self.crime_repo.count()
        total_firs = await self.fir_repo.count()
        active_firs = await self.fir_repo.count_by_status("ACTIVE")
        closed_firs = await self.fir_repo.count_by_status("INACTIVE") + await self.fir_repo.count_by_status("ARCHIVED")

        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        crimes_today = await self.crime_repo.count_by_date_range(today_str, today_str)
        firs_today = await self.fir_repo.count_by_date_range(today_str, today_str)

        registered_districts = await self.district_repo.count()
        registered_police_stations = await self.police_station_repo.count()

        return DashboardSummaryResponse(
            total_crimes=total_crimes,
            total_firs=total_firs,
            active_firs=active_firs,
            closed_firs=closed_firs,
            crimes_today=crimes_today,
            firs_today=firs_today,
            registered_districts=registered_districts,
            registered_police_stations=registered_police_stations,
        )

    async def get_recent_crimes(self, officer: Dict[str, Any], limit: int = 10) -> List[RecentCrimeResponse]:
        """Returns the most recent crimes."""
        crimes = await self.crime_repo.find_all(limit=limit, next_token=None)
        crimes_sorted = sorted(crimes, key=lambda c: c.get("CREATEDTIME", ""), reverse=True)
        return [
            RecentCrimeResponse(
                ROWID=c.get("ROWID", ""),
                title=c.get("title", ""),
                crime_type=c.get("crime_type", ""),
                status=c.get("status", ""),
                CREATEDTIME=c.get("CREATEDTIME", ""),
            )
            for c in crimes_sorted[:limit]
        ]

    async def get_recent_firs(self, officer: Dict[str, Any], limit: int = 10) -> List[RecentFirResponse]:
        """Returns the most recent FIRs."""
        firs = await self.fir_repo.find_all(limit=limit, next_token=None)
        firs_sorted = sorted(firs, key=lambda f: f.get("CREATEDTIME", ""), reverse=True)
        return [
            RecentFirResponse(
                ROWID=f.get("ROWID", ""),
                fir_number=f.get("fir_number", ""),
                crime_id=f.get("crime_id", ""),
                status=f.get("status", ""),
                CREATEDTIME=f.get("CREATEDTIME", ""),
            )
            for f in firs_sorted[:limit]
        ]

    async def get_crime_trends(self, officer: Dict[str, Any], interval: str = "daily") -> List[CrimeTrendResponse]:
        """Returns aggregated crime counts by day, week, or month."""
        all_crimes = await self.crime_repo.find_all(limit=10000)

        buckets: Dict[str, int] = {}
        for c in all_crimes:
            created = c.get("CREATEDTIME", "")
            if not created:
                continue
            try:
                dt = datetime.strptime(created[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                continue

            if interval == "daily":
                key = dt.strftime("%Y-%m-%d")
            elif interval == "weekly":
                key = dt.strftime("%Y-W%W")
            elif interval == "monthly":
                key = dt.strftime("%Y-%m")
            else:
                key = dt.strftime("%Y-%m-%d")

            buckets[key] = buckets.get(key, 0) + 1

        return [CrimeTrendResponse(period=key, count=count) for key, count in sorted(buckets.items())]

    async def get_district_summary(self, officer: Dict[str, Any]) -> List[DistrictSummaryResponse]:
        """Returns per-district crime and FIR aggregates."""
        all_crimes = await self.crime_repo.find_all(limit=10000)
        all_firs = await self.fir_repo.find_all(limit=10000)

        district_map: Dict[str, Dict[str, Any]] = {}

        for c in all_crimes:
            did = c.get("district_id", "UNKNOWN")
            if did not in district_map:
                district_map[did] = {
                    "district_name": did,
                    "crime_count": 0,
                    "fir_count": 0,
                    "active_investigations": 0,
                }
            district_map[did]["crime_count"] += 1
            if c.get("status") == "ACTIVE":
                district_map[did]["active_investigations"] += 1

        for f in all_firs:
            did = f.get("district_id", "UNKNOWN")
            if did not in district_map:
                district_map[did] = {
                    "district_name": did,
                    "crime_count": 0,
                    "fir_count": 0,
                    "active_investigations": 0,
                }
            district_map[did]["fir_count"] += 1

        return [
            DistrictSummaryResponse(
                district_id=did,
                district_name=data["district_name"],
                crime_count=data["crime_count"],
                fir_count=data["fir_count"],
                active_investigations=data["active_investigations"],
            )
            for did, data in district_map.items()
        ]

    async def get_statistics(self, officer: Dict[str, Any]) -> Dict[str, Any]:
        """Returns aggregated statistics compatible with legacy callers."""
        all_crimes = await self.crime_repo.find_all(limit=10000)
        all_firs = await self.fir_repo.find_all(limit=10000)

        category_counts: Dict[str, int] = {}
        status_counts: Dict[str, int] = {}
        district_counts: Dict[str, int] = {}

        for c in all_crimes:
            ct = c.get("crime_type", "UNKNOWN")
            category_counts[ct] = category_counts.get(ct, 0) + 1
            st = c.get("status", "ACTIVE")
            status_counts[st] = status_counts.get(st, 0) + 1
            did = c.get("district_id", "UNKNOWN")
            district_counts[did] = district_counts.get(did, 0) + 1

        total_count = sum(v for v in category_counts.values())

        by_district = [
            {"district_id": k, "district_name": k, "count": v}
            for k, v in district_counts.items()
        ]

        return {
            "by_category": [{"crime_type": k, "count": v} for k, v in category_counts.items()],
            "by_district": by_district,
            "by_status": [{"status": k, "count": v} for k, v in status_counts.items()],
            "total_count": total_count,
        }
