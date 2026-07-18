from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timezone, timedelta

from app.database.postgres.connection import get_db
from app.models.officer import Officer
from app.models.district import District
from app.api.deps import get_current_officer
from app.schemas.district_analytics import DistrictRollupResponse, DistrictTrend
from app.repositories.dashboard_repo import DashboardRepository
from app.models.enums import Role

router = APIRouter()

@router.get(
    "/{district_id}/analytics",
    response_model=DistrictRollupResponse,
    summary="Get District Analytics",
    description="Retrieves district-level rollups and comparisons (if officer roles permit)."
)
async def get_district_analytics(
    district_id: str,
    start_date: Optional[datetime] = Query(None, description="Start date (UTC)"),
    end_date: Optional[datetime] = Query(None, description="End date (UTC)"),
    db: AsyncSession = Depends(get_db),
    current_user: Officer = Depends(get_current_officer)
):
    try:
        # Check if the district exists
        district_query = select(District).where(District.id == district_id)
        result = await db.execute(district_query)
        district = result.scalar_one_or_none()
        if not district:
            raise HTTPException(status_code=404, detail="District not found")
            
        repo = DashboardRepository(db)
        stats = await repo.get_statistics(current_user, start_date=start_date, end_date=end_date)
        
        # Extract total crimes for THIS district
        total_crimes = 0
        for ds in stats.by_district:
            if ds.district_id == district_id:
                total_crimes = ds.count
                break
                
        comparisons = None
        # If user has state-wide view, provide comparisons to other districts
        if current_user.role in [Role.STATE_COMMAND, Role.SYSTEM_ADMINISTRATOR, Role.CID_ANALYST, Role.RANGE_IG]:
            comparisons = []
            for ds in stats.by_district:
                if ds.district_id != district_id:
                    # In a real app, calculate trend percentage between periods.
                    # For this scaffold, we just return the counts from the current stats
                    comparisons.append(DistrictTrend(
                        district_id=ds.district_id,
                        district_name=ds.district_name,
                        current_count=ds.count,
                        trend_direction="FLAT", # Mock placeholder for trend
                        trend_percentage=0.0
                    ))

        return DistrictRollupResponse(
            district_id=district_id,
            district_name=district.name,
            total_crimes=total_crimes,
            comparisons=comparisons
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch district analytics: {str(e)}"
        )
