from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timezone, timedelta

from app.database.postgres.connection import get_db
from app.models.officer import Officer
from app.models.crime import Crime
from app.schemas.hotspot import HotspotResponse
from app.analytics.hotspot.clustering import generate_grid_clusters
from app.api.deps import get_current_officer
from app.repositories.dashboard_repo import DashboardRepository

router = APIRouter()

@router.get(
    "/",
    response_model=HotspotResponse,
    summary="Get Crime Hotspots",
    description="Retrieves geographic clusters of crimes scoped by jurisdiction."
)
async def get_hotspots(
    start_date: Optional[datetime] = Query(None, description="Start date (UTC)"),
    end_date: Optional[datetime] = Query(None, description="End date (UTC)"),
    db: AsyncSession = Depends(get_db),
    current_user: Officer = Depends(get_current_officer)
):
    try:
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=30)
            
        repo = DashboardRepository(db)
        base_query = select(Crime).where(Crime.is_deleted == False, Crime.incident_date >= start_date, Crime.incident_date <= end_date)
        scoped_query = repo._apply_jurisdiction_scope(base_query, current_user)
        
        result = await db.execute(scoped_query)
        crimes = result.scalars().all()
        
        clusters = generate_grid_clusters(list(crimes))
        
        return HotspotResponse(
            clusters=clusters,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch hotspots: {str(e)}"
        )

from app.schemas.prediction import HotspotPredictionResponse
from app.analytics.prediction.hotspot_model import predict_hotspots

@router.get(
    "/predict",
    response_model=HotspotPredictionResponse,
    summary="Predict Emerging Hotspots",
    description="Predicts future crime hotspots based on recent trend momentum."
)
async def get_hotspot_predictions(
    db: AsyncSession = Depends(get_db),
    current_user: Officer = Depends(get_current_officer)
):
    try:
        # Current 30 days
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)
        
        # Past 30 days (for momentum comparison)
        past_end = start_date
        past_start = past_end - timedelta(days=30)
        
        repo = DashboardRepository(db)
        
        # Fetch current
        base_query = select(Crime).where(Crime.is_deleted == False, Crime.incident_date >= start_date, Crime.incident_date <= end_date)
        scoped_query = repo._apply_jurisdiction_scope(base_query, current_user)
        current_result = await db.execute(scoped_query)
        current_crimes = current_result.scalars().all()
        current_clusters = generate_grid_clusters(list(current_crimes))
        
        # Fetch past
        past_query = select(Crime).where(Crime.is_deleted == False, Crime.incident_date >= past_start, Crime.incident_date <= past_end)
        scoped_past_query = repo._apply_jurisdiction_scope(past_query, current_user)
        past_result = await db.execute(scoped_past_query)
        past_crimes = past_result.scalars().all()
        past_clusters = generate_grid_clusters(list(past_crimes))
        
        # Predict
        predictions = predict_hotspots(current_clusters, past_clusters, timeframe_days=7)
        
        return HotspotPredictionResponse(predictions=predictions)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to predict hotspots: {str(e)}"
        )
