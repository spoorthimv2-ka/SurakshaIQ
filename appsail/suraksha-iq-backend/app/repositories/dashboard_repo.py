import uuid
from typing import Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.crime import Crime, CrimeStatus
from app.models.district import District
from app.models.officer import Officer
from app.models.police_station import PoliceStation
from app.models.enums import Role
from app.schemas.dashboard import (
    DashboardKPIsResponse,
    KPIDelta,
    DashboardStatisticsResponse,
    CrimeCategoryStats,
    DistrictStats,
    StatusStats,
)

class DashboardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _apply_jurisdiction_scope(self, query, officer: Officer):
        """
        Applies row-level security (RLS) equivalent based on officer role and jurisdiction.
        """
        if officer.role in [Role.STATE_COMMAND, Role.SYSTEM_ADMINISTRATOR, Role.CID_ANALYST]:
            # State-wide access, no filter
            return query
            
        elif officer.role == Role.RANGE_IG:
            # Range IG ideally has a region_code. For now, assume state-wide or map correctly if region exists.
            # Assuming state-wide for this scaffold unless region_code is on officer.
            return query
            
        elif officer.role == Role.DISTRICT_SP:
            # Requires district_id. Since Officer links to PoliceStation,
            # we must join PoliceStation to check if it matches the officer's PoliceStation's district.
            # In a real app, Officer might have a direct district_id for SPs.
            if officer.police_station_id:
                # We need to filter crimes by the district of the officer's police station
                # query must already have Crime in context
                query = query.join(PoliceStation, Crime.police_station_id == PoliceStation.id)
                
                # Subquery to find the district_id of the officer's station
                # (For simplicity here, assuming the route layer or middleware could provide district_id, 
                # but we'll do it via join if needed. Actually, joining PoliceStation and checking its district is safer.)
                # However, sqlalchemy allows filtering if we join. We need the actual district_id.
                # A cleaner way: filter(Crime.district_id == select(PoliceStation.district_id).where(PoliceStation.id == officer.police_station_id).scalar_subquery())
                subq = select(PoliceStation.district_id).where(PoliceStation.id == officer.police_station_id).scalar_subquery()
                query = query.where(Crime.district_id == subq)
            return query
            
        elif officer.role in [Role.STATION_HOUSE_OFFICER, Role.INVESTIGATING_OFFICER]:
            if officer.police_station_id:
                return query.where(Crime.police_station_id == officer.police_station_id)
            return query
            
        return query

    async def get_kpis(self, officer: Officer, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> DashboardKPIsResponse:
        # Defaults
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=30)
            
        # Prior period for delta
        duration = end_date - start_date
        prior_start = start_date - duration
        prior_end = start_date
        
        # 1. Total Cases
        base_query = select(func.count(Crime.id)).where(Crime.is_deleted == False)
        base_query = self._apply_jurisdiction_scope(base_query, officer)
        
        current_cases_q = base_query.where(and_(Crime.incident_date >= start_date, Crime.incident_date <= end_date))
        prior_cases_q = base_query.where(and_(Crime.incident_date >= prior_start, Crime.incident_date <= prior_end))
        
        current_cases_result = await self.db.execute(current_cases_q)
        current_cases = current_cases_result.scalar() or 0
        
        prior_cases_result = await self.db.execute(prior_cases_q)
        prior_cases = prior_cases_result.scalar() or 0
        
        cases_delta = ((current_cases - prior_cases) / prior_cases * 100) if prior_cases > 0 else (100.0 if current_cases > 0 else 0.0)
        
        # 2. Resolution Rate (Closed / Total)
        current_closed_q = current_cases_q.where(Crime.status == CrimeStatus.CLOSED)
        current_closed_result = await self.db.execute(current_closed_q)
        current_closed = current_closed_result.scalar() or 0
        
        prior_closed_q = prior_cases_q.where(Crime.status == CrimeStatus.CLOSED)
        prior_closed_result = await self.db.execute(prior_closed_q)
        prior_closed = prior_closed_result.scalar() or 0
        
        current_resolution = (current_closed / current_cases * 100) if current_cases > 0 else 0.0
        prior_resolution = (prior_closed / prior_cases * 100) if prior_cases > 0 else 0.0
        resolution_delta = current_resolution - prior_resolution

        # Active Hotspots, Open Alerts, Risk Index (placeholders as per plan)
        return DashboardKPIsResponse(
            total_cases=KPIDelta(value=float(current_cases), delta=round(cases_delta, 1)),
            resolution_rate=KPIDelta(value=round(current_resolution, 1), delta=round(resolution_delta, 1)),
            active_hotspots=KPIDelta(value=0, delta=0.0),
            open_alerts=KPIDelta(value=0, delta=0.0),
            risk_index=KPIDelta(value=0, delta=0.0)
        )

    async def get_statistics(self, officer: Officer, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> DashboardStatisticsResponse:
        # Defaults
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=30)
            
        base_query = select(Crime).where(Crime.is_deleted == False, Crime.incident_date >= start_date, Crime.incident_date <= end_date)
        base_query = self._apply_jurisdiction_scope(base_query, officer)
        
        # By Category
        cat_q = base_query.with_only_columns(Crime.crime_type, func.count(Crime.id)).group_by(Crime.crime_type)
        cat_result = await self.db.execute(cat_q)
        by_category = [CrimeCategoryStats(crime_type=row[0], count=row[1]) for row in cat_result.all()]
        
        # By District
        dist_q = (
            select(District.id, District.name, func.count(Crime.id))
            .join(Crime, Crime.district_id == District.id)
            .where(Crime.is_deleted == False, Crime.incident_date >= start_date, Crime.incident_date <= end_date)
        )
        dist_q = self._apply_jurisdiction_scope(dist_q, officer)
        dist_q = dist_q.group_by(District.id, District.name)
        dist_result = await self.db.execute(dist_q)
        by_district = [DistrictStats(district_id=row[0], district_name=row[1], count=row[2]) for row in dist_result.all()]
        
        # By Status
        status_q = base_query.with_only_columns(Crime.status, func.count(Crime.id)).group_by(Crime.status)
        status_result = await self.db.execute(status_q)
        by_status = [StatusStats(status=row[0].value if hasattr(row[0], 'value') else str(row[0]), count=row[1]) for row in status_result.all()]
        
        total_count = sum([s.count for s in by_category])

        return DashboardStatisticsResponse(
            by_category=by_category,
            by_district=by_district,
            by_status=by_status,
            total_count=total_count
        )

    async def get_daily_counts(self, officer: Officer, start_date: datetime, end_date: datetime) -> list[tuple[datetime, int]]:
        """Returns daily aggregated crime counts for forecasting inputs."""
        base_query = select(func.date_trunc('day', Crime.incident_date).label('day'), func.count(Crime.id)) \
            .where(Crime.is_deleted == False, Crime.incident_date >= start_date, Crime.incident_date <= end_date)
            
        base_query = self._apply_jurisdiction_scope(base_query, officer)
        base_query = base_query.group_by('day').order_by('day')
        
        result = await self.db.execute(base_query)
        # Returns list of (datetime, count)
        return [(row[0], row[1]) for row in result.all()]
