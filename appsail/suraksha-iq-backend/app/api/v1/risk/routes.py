from fastapi import Request,  APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any, List

from app.api.deps import get_current_officer
from app.services.predictive_risk_service import PredictiveRiskService
from app.schemas.risk import (
    RiskPrediction,
    RiskSummary,
    DistrictRisk,
    StationRisk,
)

router = APIRouter()


@router.get(
    "/",
    response_model=List[RiskPrediction],
    summary="Get Risk Predictions",
    description="Retrieves risk predictions for districts and police stations.",
)
async def get_risk_predictions(
    request: Request,
    limit: int = Query(100, ge=1, le=500),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves risk predictions from Catalyst Data Store."""
    try:
        service = PredictiveRiskService(request)
        predictions = await service.get_predictions(current_user, limit=limit)
        return predictions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch risk predictions: {str(e)}"
        )


@router.get(
    "/summary",
    response_model=RiskSummary,
    summary="Get Risk Summary",
    description="Retrieves aggregated risk summary.",
)
async def get_risk_summary(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves risk summary from Catalyst Data Store."""
    try:
        service = PredictiveRiskService(request)
        summary = await service.get_summary(current_user)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch risk summary: {str(e)}"
        )


@router.get(
    "/districts",
    response_model=List[DistrictRisk],
    summary="Get District Risk",
    description="Retrieves risk predictions for all districts.",
)
async def get_district_risk(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves district risk from Catalyst Data Store."""
    try:
        service = PredictiveRiskService(request)
        districts = await service.get_district_predictions(current_user)
        return districts
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch district risk: {str(e)}"
        )


@router.get(
    "/stations",
    response_model=List[StationRisk],
    summary="Get Station Risk",
    description="Retrieves risk predictions for all police stations.",
)
async def get_station_risk(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves station risk from Catalyst Data Store."""
    try:
        service = PredictiveRiskService(request)
        stations = await service.get_station_predictions(current_user)
        return stations
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch station risk: {str(e)}"
        )


@router.get(
    "/{entity_id}",
    response_model=RiskPrediction,
    summary="Get Entity Risk",
    description="Retrieves risk prediction for a specific entity.",
)
async def get_entity_risk(
    request: Request,
    entity_id: str,
    entity_type: str = Query("District", description="Entity type: District or PoliceStation"),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves entity risk from Catalyst Data Store."""
    try:
        service = PredictiveRiskService(request)
        prediction = await service.get_entity_prediction(current_user, entity_id, entity_type)
        if not prediction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entity not found"
            )
        return prediction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch entity risk: {str(e)}"
        )
