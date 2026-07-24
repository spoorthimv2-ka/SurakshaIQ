from fastapi import Request, APIRouter, Depends, Query, HTTPException, status
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

router = APIRouter()


def _build_filters(
    jurisdiction: Optional[str] = Query(None),
    district_id: Optional[str] = Query(None),
    police_station: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    case_category: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    crime_status: Optional[str] = Query(None),
    time_preset: Optional[str] = Query(None),
) -> Dict[str, Any]:
    filters: Dict[str, Any] = {}
    if jurisdiction:
        filters["jurisdiction"] = jurisdiction
    if district_id:
        filters["district_id"] = district_id
    if police_station:
        filters["police_station"] = police_station
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date
    if case_category:
        filters["case_category"] = [c.strip() for c in case_category.split(",") if c.strip()]
    if severity:
        filters["severity"] = severity
    if crime_status:
        filters["crime_status"] = crime_status
    if time_preset:
        filters["time_preset"] = time_preset
    return filters


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Get Dashboard Summary",
    description="Retrieves high-level dashboard summary counts.",
)
async def get_dashboard_summary(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_officer),
    filters: Dict[str, Any] = Depends(_build_filters),
):
    """Retrieves dashboard summary from Catalyst Data Store."""
    try:
        service = DashboardService(request)
        summary = await service.get_summary(current_user, filters=filters)
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
    request: Request,
    limit: int = Query(10, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_officer),
    filters: Dict[str, Any] = Depends(_build_filters),
):
    """Retrieves recent crimes from Catalyst Data Store."""
    try:
        service = DashboardService(request)
        crimes = await service.get_recent_crimes(current_user, limit=limit, filters=filters)
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
    request: Request,
    limit: int = Query(10, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_officer),
    filters: Dict[str, Any] = Depends(_build_filters),
):
    """Retrieves recent FIRs from Catalyst Data Store."""
    try:
        service = DashboardService(request)
        firs = await service.get_recent_firs(current_user, limit=limit, filters=filters)
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
    request: Request,
    interval: str = Query("daily", description="Aggregation interval: daily, weekly, or monthly"),
    current_user: Dict[str, Any] = Depends(get_current_officer),
    filters: Dict[str, Any] = Depends(_build_filters),
):
    """Retrieves crime trends from Catalyst Data Store."""
    try:
        if interval not in ("daily", "weekly", "monthly", "quarterly", "yearly"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid interval. Use daily, weekly, monthly, quarterly, or yearly.")
        service = DashboardService(request)
        trends = await service.get_crime_trends(current_user, interval=interval, filters=filters)
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
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_officer),
    filters: Dict[str, Any] = Depends(_build_filters),
):
    """Retrieves district summary from Catalyst Data Store."""
    try:
        service = DashboardService(request)
        summary = await service.get_district_summary(current_user, filters=filters)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch district summary: {str(e)}"
        )