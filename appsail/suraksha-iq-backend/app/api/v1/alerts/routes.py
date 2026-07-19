from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any, List

from app.api.deps import get_current_officer
from app.services.alert_service import AlertService
from app.schemas.alert import AlertResponse, AlertSummary, AlertStatistics

router = APIRouter()


@router.get(
    "/",
    response_model=List[AlertResponse],
    summary="Get Alerts",
    description="Retrieves a list of alerts with optional filters.",
)
async def get_alerts(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (e.g. ACTIVE)"),
    severity: Optional[str] = Query(None, description="Filter by severity (e.g. HIGH)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves alerts scoped by jurisdiction."""
    try:
        service = AlertService(AlertRepository())
        alerts = await service.get_alerts(status_filter=status_filter, severity=severity, limit=limit, offset=offset)
        return [AlertResponse.model_validate(a) for a in alerts]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch alerts: {str(e)}"
        )


@router.get(
    "/summary",
    response_model=AlertSummary,
    summary="Get Alert Summary",
    description="Retrieves alert summary counts.",
)
async def get_alert_summary(
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves alert summary from Catalyst Data Store."""
    try:
        service = AlertService(AlertRepository())
        summary = await service.get_summary()
        return AlertSummary(**summary)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch alert summary: {str(e)}"
        )


@router.get(
    "/active",
    response_model=List[AlertResponse],
    summary="Get Active Alerts",
    description="Retrieves active alerts.",
)
async def get_active_alerts(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves active alerts from Catalyst Data Store."""
    try:
        service = AlertService(AlertRepository())
        alerts = await service.get_active_alerts(limit=limit, offset=offset)
        return [AlertResponse.model_validate(a) for a in alerts]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch active alerts: {str(e)}"
        )


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
    summary="Get Alert by ID",
    description="Retrieves a single alert by its ROWID.",
)
async def get_alert(
    alert_id: str,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves an alert by ID."""
    try:
        service = AlertService(AlertRepository())
        alert = await service.get_by_id(alert_id)
        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
        return AlertResponse.model_validate(alert)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch alert: {str(e)}"
        )


@router.post(
    "/{alert_id}/acknowledge",
    response_model=AlertResponse,
    summary="Acknowledge Alert",
    description="Acknowledges an alert.",
)
async def acknowledge_alert(
    alert_id: str,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Acknowledges an alert."""
    try:
        service = AlertService(AlertRepository())
        result = await service.acknowledge_alert(alert_id)
        return AlertResponse.model_validate(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to acknowledge alert: {str(e)}"
        )


@router.post(
    "/{alert_id}/resolve",
    response_model=AlertResponse,
    summary="Resolve Alert",
    description="Resolves an alert.",
)
async def resolve_alert(
    alert_id: str,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Resolves an alert."""
    try:
        service = AlertService(AlertRepository())
        result = await service.resolve_alert(alert_id)
        return AlertResponse.model_validate(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve alert: {str(e)}"
        )
