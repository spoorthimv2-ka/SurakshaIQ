from fastapi import Request,  APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any, List

from app.api.deps import get_current_officer
from app.services.anomaly_service import AnomalyService
from app.schemas.anomaly import Anomaly, AnomalySummary, DistrictAnomaly, StationAnomaly

router = APIRouter()


@router.get(
    "/",
    response_model=List[Anomaly],
    summary="Get Anomalies",
    description="Retrieves detected anomalies for districts and police stations.",
)
async def get_anomalies(
    request: Request,
    limit: int = Query(100, ge=1, le=500),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves anomalies from Catalyst Data Store."""
    try:
        service = AnomalyService(request)
        anomalies = await service.get_anomalies(current_user, limit=limit)
        return anomalies
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch anomalies: {str(e)}"
        )


@router.get(
    "/summary",
    response_model=AnomalySummary,
    summary="Get Anomaly Summary",
    description="Retrieves aggregated anomaly summary.",
)
async def get_anomaly_summary(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves anomaly summary from Catalyst Data Store."""
    try:
        service = AnomalyService(request)
        summary = await service.get_summary(current_user)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch anomaly summary: {str(e)}"
        )


@router.get(
    "/districts",
    response_model=List[DistrictAnomaly],
    summary="Get District Anomalies",
    description="Retrieves anomalies for all districts.",
)
async def get_district_anomalies(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves district anomalies from Catalyst Data Store."""
    try:
        service = AnomalyService(request)
        districts = await service.get_district_anomalies(current_user)
        return districts
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch district anomalies: {str(e)}"
        )


@router.get(
    "/stations",
    response_model=List[StationAnomaly],
    summary="Get Station Anomalies",
    description="Retrieves anomalies for all police stations.",
)
async def get_station_anomalies(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves station anomalies from Catalyst Data Store."""
    try:
        service = AnomalyService(request)
        stations = await service.get_station_anomalies(current_user)
        return stations
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch station anomalies: {str(e)}"
        )


@router.get(
    "/{anomaly_id}",
    response_model=Anomaly,
    summary="Get Anomaly Details",
    description="Retrieves details for a specific anomaly.",
)
async def get_anomaly(
    request: Request,
    anomaly_id: str,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves anomaly details from Catalyst Data Store."""
    try:
        service = AnomalyService(request)
        anomaly = await service.get_anomaly(current_user, anomaly_id)
        if not anomaly:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Anomaly not found"
            )
        return anomaly
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch anomaly: {str(e)}"
        )
