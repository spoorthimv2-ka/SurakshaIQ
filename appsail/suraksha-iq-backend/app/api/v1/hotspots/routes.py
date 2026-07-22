from fastapi import Request,  APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta

from app.api.deps import get_current_officer
from app.services.hotspot_service import HotspotService
from app.schemas.hotspot import (
    HotspotResponse,
    DistrictHotspotResponse,
    StationHotspotResponse,
    HotspotSummaryResponse,
)

router = APIRouter()


@router.get(
    "/",
    response_model=List[HotspotResponse],
    summary="Get Crime Hotspots",
    description="Retrieves hotspot records with optional filters.",
)
async def get_hotspots(
    request: Request,
    district_id: Optional[str] = Query(None, description="Filter by district ID"),
    station_id: Optional[str] = Query(None, description="Filter by police station ID"),
    crime_type: Optional[str] = Query(None, description="Filter by crime type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Start date (UTC)"),
    end_date: Optional[datetime] = Query(None, description="End date (UTC)"),
    limit: int = Query(100, ge=1, le=500),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves hotspot data from Catalyst Data Store."""
    try:
        service = HotspotService(request)
        hotspots = await service.get_hotspots(
            current_user,
            district_id=district_id,
            station_id=station_id,
            crime_type=crime_type,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
        return hotspots
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch hotspots: {str(e)}"
        )


@router.get(
    "/districts",
    response_model=List[DistrictHotspotResponse],
    summary="Get District Hotspots",
    description="Retrieves hotspot summary per district.",
)
async def get_district_hotspots(
    request: Request,
    start_date: Optional[datetime] = Query(None, description="Start date (UTC)"),
    end_date: Optional[datetime] = Query(None, description="End date (UTC)"),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves district hotspot summary from Catalyst Data Store."""
    try:
        service = HotspotService(request)
        hotspots = await service.get_district_hotspots(current_user, start_date=start_date, end_date=end_date)
        return hotspots
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch district hotspots: {str(e)}"
        )


@router.get(
    "/stations",
    response_model=List[StationHotspotResponse],
    summary="Get Station Hotspots",
    description="Retrieves hotspot summary per police station.",
)
async def get_station_hotspots(
    request: Request,
    start_date: Optional[datetime] = Query(None, description="Start date (UTC)"),
    end_date: Optional[datetime] = Query(None, description="End date (UTC)"),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves station hotspot summary from Catalyst Data Store."""
    try:
        service = HotspotService(request)
        hotspots = await service.get_station_hotspots(current_user, start_date=start_date, end_date=end_date)
        return hotspots
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch station hotspots: {str(e)}"
        )


@router.get(
    "/top",
    response_model=List[HotspotResponse],
    summary="Get Top Hotspots",
    description="Returns the highest-ranked hotspots.",
)
async def get_top_hotspots(
    request: Request,
    limit: int = Query(10, ge=1, le=100),
    start_date: Optional[datetime] = Query(None, description="Start date (UTC)"),
    end_date: Optional[datetime] = Query(None, description="End date (UTC)"),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves top hotspots from Catalyst Data Store."""
    try:
        service = HotspotService(request)
        hotspots = await service.get_top_hotspots(current_user, limit=limit, start_date=start_date, end_date=end_date)
        return hotspots
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch top hotspots: {str(e)}"
        )

