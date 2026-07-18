from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.database.postgres.connection import get_db
from app.models.officer import Officer
from app.schemas.dashboard import DashboardKPIsResponse, DashboardStatisticsResponse
from app.repositories.dashboard_repo import DashboardRepository
from app.api.deps import get_current_officer
from app.models.enums import Permission

router = APIRouter()

@router.get(
    "/kpis",
    response_model=DashboardKPIsResponse,
    summary="Get Dashboard KPIs",
    description="Retrieves key performance indicators for the dashboard, scoped by the requesting officer's jurisdiction."
)
async def get_dashboard_kpis(
    start_date: Optional[datetime] = Query(None, description="Start date for KPI filtering (UTC)"),
    end_date: Optional[datetime] = Query(None, description="End date for KPI filtering (UTC)"),
    db: AsyncSession = Depends(get_db),
    current_user: Officer = Depends(get_current_officer)
):
    try:
        repo = DashboardRepository(db)
        kpis = await repo.get_kpis(current_user, start_date, end_date)
        return kpis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch KPIs: {str(e)}"
        )

@router.get(
    "/statistics",
    response_model=DashboardStatisticsResponse,
    summary="Get Dashboard Statistics",
    description="Retrieves aggregated crime statistics broken down by category, district, and status."
)
async def get_dashboard_statistics(
    start_date: Optional[datetime] = Query(None, description="Start date for statistics filtering (UTC)"),
    end_date: Optional[datetime] = Query(None, description="End date for statistics filtering (UTC)"),
    db: AsyncSession = Depends(get_db),
    current_user: Officer = Depends(get_current_officer)
):
    try:
        repo = DashboardRepository(db)
        stats = await repo.get_statistics(current_user, start_date, end_date)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch statistics: {str(e)}"
        )

from app.schemas.forecast import ForecastResponse
from app.analytics.prediction.trend_model import generate_trend_forecast
from datetime import timezone, timedelta

@router.get(
    "/forecast",
    response_model=ForecastResponse,
    summary="Get Crime Trend Forecast",
    description="Forecasts future crime trends based on historical counts and jurisdiction scoping."
)
async def get_dashboard_forecast(
    horizon_days: int = Query(7, ge=1, le=30, description="Days to forecast into the future"),
    db: AsyncSession = Depends(get_db),
    current_user: Officer = Depends(get_current_officer)
):
    try:
        # Use past 90 days as baseline for the SMA
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=90)
        
        repo = DashboardRepository(db)
        daily_counts = await repo.get_daily_counts(current_user, start_date, end_date)
        
        forecast_points = generate_trend_forecast(daily_counts, horizon_days=horizon_days)
        
        return ForecastResponse(
            category="total_crimes",
            horizon_days=horizon_days,
            data=forecast_points
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate forecast: {str(e)}"
        )
