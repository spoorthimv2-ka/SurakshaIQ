from fastapi import Request,  APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta

from app.api.deps import get_current_officer
from app.services.repeat_offender_service import RepeatOffenderService
from app.schemas.repeat_offender import (
    RepeatOffenderResponse,
    RepeatOffenderDetailResponse,
    OffenceTimelineItem,
    RepeatOffenderStatisticsResponse,
)

router = APIRouter()


@router.get(
    "/",
    response_model=List[RepeatOffenderResponse],
    summary="Get Repeat Offenders",
    description="Retrieves a paginated list of repeat offenders with optional filters. Uses explicit CrimeCriminalLink by default.",
)
async def get_repeat_offenders(
    request: Request,
    district_id: Optional[str] = Query(None, description="Filter by district ID"),
    station_id: Optional[str] = Query(None, description="Filter by police station ID"),
    crime_type: Optional[str] = Query(None, description="Filter by crime type"),
    start_date: Optional[datetime] = Query(None, description="Start date (UTC)"),
    end_date: Optional[datetime] = Query(None, description="End date (UTC)"),
    minimum_offences: int = Query(1, ge=1, description="Minimum offences threshold"),
    include_heuristic: bool = Query(False, description="Include district-proximity heuristic matching"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves repeat offenders from Catalyst Data Store."""
    try:
        service = RepeatOffenderService(request)
        offenders = await service.get_repeat_offenders(
            current_user,
            district_id=district_id,
            station_id=station_id,
            crime_type=crime_type,
            start_date=start_date,
            end_date=end_date,
            minimum_offences=minimum_offences,
            limit=limit,
            offset=offset,
            include_heuristic=include_heuristic,
        )
        return offenders
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch repeat offenders: {str(e)}"
        )


@router.get(
    "/top",
    response_model=List[RepeatOffenderResponse],
    summary="Get Top Repeat Offenders",
    description="Returns the highest-ranked repeat offenders.",
)
async def get_top_repeat_offenders(
    request: Request,
    limit: int = Query(10, ge=1, le=100),
    start_date: Optional[datetime] = Query(None, description="Start date (UTC)"),
    end_date: Optional[datetime] = Query(None, description="End date (UTC)"),
    include_heuristic: bool = Query(False, description="Include district-proximity heuristic matching"),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves top repeat offenders from Catalyst Data Store."""
    try:
        service = RepeatOffenderService(request)
        offenders = await service.get_top_repeat_offenders(
            current_user,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            include_heuristic=include_heuristic,
        )
        return offenders
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch top repeat offenders: {str(e)}"
        )


@router.get(
    "/statistics",
    response_model=RepeatOffenderStatisticsResponse,
    summary="Get Repeat Offender Statistics",
    description="Retrieves aggregated repeat offender statistics.",
)
async def get_repeat_offender_statistics(
    request: Request,
    start_date: Optional[datetime] = Query(None, description="Start date (UTC)"),
    end_date: Optional[datetime] = Query(None, description="End date (UTC)"),
    include_heuristic: bool = Query(False, description="Include district-proximity heuristic matching"),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves repeat offender statistics from Catalyst Data Store."""
    try:
        service = RepeatOffenderService(request)
        stats = await service.get_statistics(current_user, start_date=start_date, end_date=end_date, include_heuristic=include_heuristic)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch repeat offender statistics: {str(e)}"
        )


@router.get(
    "/{offender_id}",
    response_model=RepeatOffenderDetailResponse,
    summary="Get Repeat Offender Details",
    description="Retrieves detailed information for a specific offender.",
)
async def get_offender_details(
    request: Request,
    offender_id: str,
    include_heuristic: bool = Query(False, description="Include district-proximity heuristic matching"),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves offender details from Catalyst Data Store."""
    try:
        service = RepeatOffenderService(request)
        detail = await service.get_offender_details(current_user, offender_id, include_heuristic=include_heuristic)
        if not detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offender not found"
            )
        return detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch offender details: {str(e)}"
        )
