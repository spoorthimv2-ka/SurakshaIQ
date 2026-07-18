from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.database.postgres.connection import get_db
from app.models.officer import Officer
from app.models.alert import Alert
from app.api.deps import get_current_officer
from app.schemas.alert import AlertListResponse, AlertResponse
from app.repositories.alert_repo import AlertRepository

router = APIRouter()

@router.get(
    "/",
    response_model=AlertListResponse,
    summary="Get Alerts",
    description="Retrieves a paginated list of alerts (anomalies, hotspots, etc.) scoped by jurisdiction."
)
async def get_alerts(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (e.g. active)"),
    severity: Optional[str] = Query(None, description="Filter by severity (e.g. HIGH)"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Officer = Depends(get_current_officer)
):
    try:
        repo = AlertRepository(db)
        
        base_query = select(Alert)
        if status_filter:
            base_query = base_query.where(Alert.status == status_filter)
        if severity:
            base_query = base_query.where(Alert.severity == severity)
            
        scoped_query = repo._apply_jurisdiction_scope(base_query, current_user)
        
        # Count
        count_query = select(func.count()).select_from(scoped_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Fetch
        skip = (page - 1) * size
        fetch_query = scoped_query.order_by(Alert.created_at.desc()).offset(skip).limit(size)
        result = await db.execute(fetch_query)
        alerts = result.scalars().all()
        
        return AlertListResponse(
            data=[AlertResponse.model_validate(a) for a in alerts],
            total=total,
            page=page,
            size=size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch alerts: {str(e)}"
        )
