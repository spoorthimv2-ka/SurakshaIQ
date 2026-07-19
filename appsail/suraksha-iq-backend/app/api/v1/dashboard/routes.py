from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any, List

from app.api.deps import get_current_officer
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import (
    DashboardKPIsResponse,
    DashboardStatisticsResponse,
    DashboardSummaryResponse,
    RecentCrimeResponse,
    RecentFirResponse,
    CrimeTrendResponse,
    DistrictSummaryResponse,
)
from app.core.logger import logger

router = APIRouter()


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Get Dashboard Summary",
    description="Retrieves high-level dashboard summary counts.",
)
async def get_dashboard_summary(
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves dashboard summary from Catalyst Data Store."""
    try:
        service = DashboardService()
        summary = await service.get_summary(current_user)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch summary: {str(e)}"
        )


@router.get(
    "/recent-crimes",
    response_model=List[RecentCrimeResponse],
    summary="Get Recent Crimes",
    description="Retrieves the most recent crimes.",
)
async def get_recent_crimes(
    limit: int = Query(10, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves recent crimes from Catalyst Data Store."""
    try:
        service = DashboardService()
        crimes = await service.get_recent_crimes(current_user, limit=limit)
        return crimes
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch recent crimes: {str(e)}"
        )


@router.get(
    "/recent-firs",
    response_model=List[RecentFirResponse],
    summary="Get Recent FIRs",
    description="Retrieves the most recent FIRs.",
)
async def get_recent_firs(
    limit: int = Query(10, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves recent FIRs from Catalyst Data Store."""
    try:
        service = DashboardService()
        firs = await service.get_recent_firs(current_user, limit=limit)
        return firs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch recent FIRs: {str(e)}"
        )


@router.get(
    "/crime-trends",
    response_model=List[CrimeTrendResponse],
    summary="Get Crime Trends",
    description="Retrieves aggregated crime counts grouped by day, week, or month.",
)
async def get_crime_trends(
    interval: str = Query("daily", description="Aggregation interval: daily, weekly, or monthly"),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves crime trends from Catalyst Data Store."""
    try:
        if interval not in ("daily", "weekly", "monthly"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid interval. Use daily, weekly, or monthly.")
        service = DashboardService()
        trends = await service.get_crime_trends(current_user, interval=interval)
        return trends
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch crime trends: {str(e)}"
        )


@router.get(
    "/district-summary",
    response_model=List[DistrictSummaryResponse],
    summary="Get District Summary",
    description="Retrieves per-district crime and FIR aggregates.",
)
async def get_district_summary(
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves district summary from Catalyst Data Store."""
    try:
        service = DashboardService()
        summary = await service.get_district_summary(current_user)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch district summary: {str(e)}"
        )
