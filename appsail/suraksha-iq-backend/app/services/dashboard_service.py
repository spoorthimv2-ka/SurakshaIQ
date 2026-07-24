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

    def _apply_filters(self, items: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        filtered = items
        if filters.get("jurisdiction"):
            filtered = [i for i in filtered if i.get("jurisdiction") == filters["jurisdiction"] or i.get("district_id", "").startswith(filters["jurisdiction"].split("-")[0])]
        if filters.get("police_station"):
            filtered = [i for i in filtered if i.get("police_station_id") == filters["police_station"] or i.get("station_id") == filters["police_station"]]
        if filters.get("case_category"):
            filtered = [i for i in filtered if i.get("crime_type") in filters["case_category"]]
        if filters.get("severity"):
            filtered = [i for i in filtered if i.get("severity") == filters["severity"]]
        if filters.get("crime_status"):
            filtered = [i for i in filtered if i.get("status") == filters["crime_status"]]
        if filters.get("start_date") or filters.get("end_date"):
            start = filters.get("start_date")
            end = filters.get("end_date")
            filtered = [i for i in filtered if self._in_date_range(i.get("CREATEDTIME", ""), start, end)]
        return filtered

    def _in_date_range(self, created_time: str, start: Optional[str], end: Optional[str]) -> bool:
        if not created_time:
            return True
        try:
            dt = datetime.strptime(created_time[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return True
        if start:
            start_dt = datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if dt < start_dt:
                return False
        if end:
            end_dt = datetime.strptime(end, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if dt > end_dt:
                return False
        return True

    async def get_summary(self, officer: Dict[str, Any], filters: Optional[Dict[str, Any]] = None) -> DashboardSummaryResponse:
        """Returns high-level dashboard summary counts."""
        all_crimes = await self.crime_repo.find_all(limit=10000)
        all_firs = await self.fir_repo.find_all(limit=10000)

        filtered_crimes = self._apply_filters(all_crimes, filters or {})
        filtered_firs = self._apply_filters(all_firs, filters or {})

        total_crimes = len(filtered_crimes)
        total_firs = len(filtered_firs)
        active_firs = sum(1 for f in filtered_firs if f.get("status") == "ACTIVE")
        closed_firs = sum(1 for f in filtered_firs if f.get("status") in ("INACTIVE", "ARCHIVED"))

        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        crimes_today = sum(1 for c in filtered_crimes if c.get("CREATEDTIME", "").startswith(today_str))
        firs_today = sum(1 for f in filtered_firs if f.get("CREATEDTIME", "").startswith(today_str))

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

    async def get_recent_crimes(self, officer: Dict[str, Any], limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[RecentCrimeResponse]:
        """Returns the most recent crimes."""
        crimes = await self.crime_repo.find_all(limit=limit * 3, next_token=None)
        filtered = self._apply_filters(crimes, filters or {})
        crimes_sorted = sorted(filtered, key=lambda c: c.get("CREATEDTIME", ""), reverse=True)
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

    async def get_recent_firs(self, officer: Dict[str, Any], limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[RecentFirResponse]:
        """Returns the most recent FIRs."""
        firs = await self.fir_repo.find_all(limit=limit * 3, next_token=None)
        filtered = self._apply_filters(firs, filters or {})
        firs_sorted = sorted(filtered, key=lambda f: f.get("CREATEDTIME", ""), reverse=True)
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

    async def get_crime_trends(self, officer: Dict[str, Any], interval: str = "daily", filters: Optional[Dict[str, Any]] = None) -> List[CrimeTrendResponse]:
        """Returns aggregated crime counts by day, week, or month."""
        all_crimes = await self.crime_repo.find_all(limit=10000)
        filtered = self._apply_filters(all_crimes, filters or {})

        buckets: Dict[str, int] = {}
        for c in filtered:
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
            elif interval == "quarterly":
                key = f"{dt.year}-Q{(dt.month - 1) // 3 + 1}"
            elif interval == "yearly":
                key = dt.strftime("%Y")
            else:
                key = dt.strftime("%Y-%m-%d")

            buckets[key] = buckets.get(key, 0) + 1

        return [CrimeTrendResponse(period=key, count=count) for key, count in sorted(buckets.items())]

    async def get_district_summary(self, officer: Dict[str, Any], filters: Optional[Dict[str, Any]] = None) -> List[DistrictSummaryResponse]:
        """Returns per-district crime and FIR aggregates."""
        all_crimes = await self.crime_repo.find_all(limit=10000)
        all_firs = await self.fir_repo.find_all(limit=10000)

        filtered_crimes = self._apply_filters(all_crimes, filters or {})
        filtered_firs = self._apply_filters(all_firs, filters or {})

        district_map: Dict[str, Dict[str, Any]] = {}

        for c in filtered_crimes:
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

        for f in filtered_firs:
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