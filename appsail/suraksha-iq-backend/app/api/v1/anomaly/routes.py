from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta

from app.database.postgres.connection import get_db
from app.models.officer import Officer
from app.api.deps import get_current_officer
from app.schemas.anomaly import AnomalyDetectionResponse
from app.repositories.dashboard_repo import DashboardRepository
from app.analytics.anomaly.detector import detect_anomalies

router = APIRouter()

@router.get(
    "/detect",
    response_model=AnomalyDetectionResponse,
    summary="Detect Anomalies",
    description="Runs statistical anomaly detection over the jurisdiction's recent crime trends and syncs findings to Alerts."
)
async def run_anomaly_detection(
    db: AsyncSession = Depends(get_db),
    current_user: Officer = Depends(get_current_officer)
):
    try:
        # Fetch last 30 days for baseline
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)
        
        repo = DashboardRepository(db)
        
        # We reuse the get_daily_counts query from Phase 3C / 3E Part 1
        daily_counts = await repo.get_daily_counts(current_user, start_date, end_date)
        
        # Note: In a true multi-district scan, this would iterate over all districts.
        # For the scaffold, we pass the officer's primary district scope.
        # If the officer has state-wide scope, district_id could be None.
        
        # Ensure we don't pass an empty string, pass None if state-wide
        district_id = current_user.station.district_id if (current_user.station and getattr(current_user, 'role', '') != 'STATE_COMMAND') else None
        
        anomalies = await detect_anomalies(db, district_id, daily_counts)
        
        return AnomalyDetectionResponse(anomalies=anomalies)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run anomaly detection: {str(e)}"
        )
