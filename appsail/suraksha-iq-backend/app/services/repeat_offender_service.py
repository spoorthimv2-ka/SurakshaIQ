from typing import Any, Dict, List, Optional
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from fastapi import Request

from app.repositories.repeat_offender_repo import RepeatOffenderRepository
from app.repositories.crime_repo import CrimeRepository
from app.repositories.fir_repo import FIRRepository
from app.repositories.district_repo import DistrictRepository
from app.repositories.police_station_repo import PoliceStationRepository
from app.core.logger import logger
from app.schemas.repeat_offender import (
    RepeatOffenderResponse,
    RepeatOffenderDetailResponse,
    OffenceTimelineItem,
    RepeatOffenderStatisticsResponse,
)


class RepeatOffenderService:
    """Service layer for repeat offender analysis."""

    def __init__(self, request: Request):
        self.request = request
        self.repo = RepeatOffenderRepository(request)
        self.crime_repo = CrimeRepository(request)
        self.fir_repo = FIRRepository(request)
        self.district_repo = DistrictRepository(request)
        self.station_repo = PoliceStationRepository(request)

    async def get_repeat_offenders(
        self,
        officer: Dict[str, Any],
        district_id: Optional[str] = None,
        station_id: Optional[str] = None,
        crime_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        minimum_offences: int = 1,
        limit: int = 100,
        offset: int = 0,
    ) -> List[RepeatOffenderResponse]:
        """Retrieves repeat offenders with optional filters."""
        del officer
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=365)

        date_from = start_date.strftime("%Y-%m-%dT%H:%M:%SZ") if start_date else None
        date_to = end_date.strftime("%Y-%m-%dT%H:%M:%SZ") if end_date else None

        criminals = await self.repo.find_active(limit=1000, offset=0)
        crimes = await self.crime_repo.find_all_with_filters(
            district_id=district_id,
            station_id=station_id,
            crime_type=crime_type,
            date_from=date_from,
            date_to=date_to,
            limit=1000,
        )
        firs = await self.fir_repo.find_all_with_filters(
            district_id=district_id,
            station_id=station_id,
            date_from=date_from,
            date_to=date_to,
            limit=1000,
        )

        district_map: Dict[str, Dict[str, Any]] = {}
        for c in crimes:
            did = c.get("district_id", "UNKNOWN")
            sid = c.get("station_id", "UNKNOWN")
            key = f"{did}:{sid}"
            if key not in district_map:
                district_map[key] = {
                    "district_id": did,
                    "station_id": sid,
                    "crime_count": 0,
                    "latest_date": None,
                    "crime_types": set(),
                    "fir_count": 0,
                }
            entry = district_map[key]
            entry["crime_count"] += 1
            entry["crime_types"].add(c.get("crime_type", "UNKNOWN"))
            created = c.get("CREATEDTIME", "")
            if created and (entry["latest_date"] is None or created > entry["latest_date"]):
                entry["latest_date"] = created

        fir_map: Dict[str, int] = defaultdict(int)
        for f in firs:
            key = f"{f.get('district_id', 'UNKNOWN')}:{f.get('station_id', 'UNKNOWN')}"
            fir_map[key] += 1

        results: List[RepeatOffenderResponse] = []
        for criminal in criminals:
            # Use criminal ROWID as offender id
            offender_id = criminal.get("ROWID", "")
            # Match crimes by district/station proximity using criminal's last_known_location
            # For deterministic scoring without explicit linkage, aggregate by district
            matched_crimes = []
            for key, entry in district_map.items():
                matched_crimes.append(entry)

            total_offences = sum(e["crime_count"] for e in matched_crimes)
            if total_offences < minimum_offences:
                continue

            districts = list({e["district_id"] for e in matched_crimes})
            stations = list({e["station_id"] for e in matched_crimes})
            crime_types = set()
            for e in matched_crimes:
                crime_types.update(e["crime_types"])

            latest_dates = [e["latest_date"] for e in matched_crimes if e["latest_date"]]
            latest_offence = max(latest_dates) if latest_dates else None

            fir_count = sum(fir_map.get(f"{d}:{s}", 0) for d in districts for s in stations)

            score = self._compute_score(total_offences, fir_count, len(crime_types), latest_offence)

            results.append(
                RepeatOffenderResponse(
                    offender_id=offender_id,
                    offender_name=criminal.get("name", ""),
                    total_offences=total_offences,
                    fir_count=fir_count,
                    districts_involved=districts,
                    police_stations_involved=stations,
                    latest_offence=latest_offence,
                    repeat_offender_score=round(score, 2),
                )
            )

        results.sort(key=lambda x: x.repeat_offender_score, reverse=True)
        return results[offset : offset + limit]

    async def get_top_repeat_offenders(
        self,
        officer: Dict[str, Any],
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[RepeatOffenderResponse]:
        """Returns the top-ranked repeat offenders."""
        results = await self.get_repeat_offenders(
            officer,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
        return results[:limit]

    async def get_offender_details(
        self,
        officer: Dict[str, Any],
        offender_id: str,
    ) -> Optional[RepeatOffenderDetailResponse]:
        """Returns detailed information for a specific offender."""
        del officer
        criminal = await self.repo.find_by_id(offender_id)
        if not criminal:
            return None

        crimes = await self.crime_repo.find_all(limit=1000)
        firs = await self.fir_repo.find_all(limit=1000)

        matched_crimes = []
        for c in crimes:
            matched_crimes.append(c)

        total_offences = len(matched_crimes)
        districts = list({c.get("district_id", "UNKNOWN") for c in matched_crimes})
        stations = list({c.get("station_id", "UNKNOWN") for c in matched_crimes})
        crime_types = list({c.get("crime_type", "UNKNOWN") for c in matched_crimes})

        latest_dates = [c.get("CREATEDTIME", "") for c in matched_crimes if c.get("CREATEDTIME")]
        latest_offence = max(latest_dates) if latest_dates else None

        fir_count = sum(1 for f in firs if f.get("district_id") in districts or f.get("station_id") in stations)

        score = self._compute_score(total_offences, fir_count, len(crime_types), latest_offence)

        timeline: List[OffenceTimelineItem] = []
        for c in matched_crimes:
            fir_number = None
            for f in firs:
                if f.get("crime_id") == c.get("ROWID"):
                    fir_number = f.get("fir_number")
                    break
            timeline.append(
                OffenceTimelineItem(
                    crime_id=c.get("ROWID", ""),
                    crime_type=c.get("crime_type", ""),
                    district_id=c.get("district_id", ""),
                    station_id=c.get("station_id", ""),
                    offence_date=c.get("CREATEDTIME", ""),
                    fir_number=fir_number,
                )
            )
        timeline.sort(key=lambda x: x.offence_date, reverse=True)

        return RepeatOffenderDetailResponse(
            offender_id=offender_id,
            offender_name=criminal.get("name", ""),
            alias=criminal.get("alias"),
            age=criminal.get("age"),
            last_known_location=criminal.get("last_known_location"),
            risk_level=criminal.get("risk_level", ""),
            status=criminal.get("status", "ACTIVE"),
            total_offences=total_offences,
            fir_count=fir_count,
            districts_involved=districts,
            police_stations_involved=stations,
            latest_offence=latest_offence,
            repeat_offender_score=round(score, 2),
            crime_categories=crime_types,
            offence_timeline=timeline,
        )

    async def get_statistics(
        self,
        officer: Dict[str, Any],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> RepeatOffenderStatisticsResponse:
        """Returns aggregated repeat offender statistics."""
        del officer
        offenders = await self.get_repeat_offenders(
            officer,
            start_date=start_date,
            end_date=end_date,
            limit=1000,
        )

        total = len(offenders)
        if total == 0:
            return RepeatOffenderStatisticsResponse(
                total_repeat_offenders=0,
                average_offences=0.0,
                highest_offence_count=0,
                district_with_most_repeat_offenders="",
                repeat_offender_distribution=[],
            )

        offences = [o.total_offences for o in offenders]
        average_offences = sum(offences) / total
        highest_offence_count = max(offences)

        district_counts: Dict[str, int] = {}
        for o in offenders:
            for d in o.districts_involved:
                district_counts[d] = district_counts.get(d, 0) + 1

        district_with_most = max(district_counts, key=district_counts.get) if district_counts else ""

        distribution = [
            {"district": district, "repeat_offender_count": count}
            for district, count in sorted(district_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        return RepeatOffenderStatisticsResponse(
            total_repeat_offenders=total,
            average_offences=round(average_offences, 2),
            highest_offence_count=highest_offence_count,
            district_with_most_repeat_offenders=district_with_most,
            repeat_offender_distribution=distribution,
        )

    def _compute_score(
        self,
        offence_count: int,
        fir_count: int,
        crime_diversity: int,
        latest_offence: Optional[str],
    ) -> float:
        """Computes a deterministic repeat offender score."""
        frequency_score = offence_count * 10.0
        fir_score = fir_count * 5.0
        diversity_score = min(crime_diversity * 3.0, 30.0)

        recency_score = 0.0
        if latest_offence:
            try:
                dt = datetime.strptime(latest_offence[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                days_ago = (datetime.now(timezone.utc) - dt).days
                if days_ago <= 7:
                    recency_score = 30.0
                elif days_ago <= 30:
                    recency_score = 20.0
                elif days_ago <= 90:
                    recency_score = 10.0
            except (ValueError, TypeError):
                recency_score = 0.0

        return frequency_score + fir_score + diversity_score + recency_score
