from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.database.postgres.connection import get_db
from app.models.officer import Officer
from app.models.report import Report
from app.api.deps import get_current_officer
from app.schemas.report import ReportListResponse, ReportResponse, ReportDetailResponse

router = APIRouter()

@router.get(
    "/",
    response_model=ReportListResponse,
    summary="Get Reports",
    description="Retrieves a paginated list of report configurations."
)
async def get_reports(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Officer = Depends(get_current_officer)
):
    try:
        # Simplest scoping: users only see their own saved reports.
        # Could be expanded based on jurisdiction rules if needed.
        base_query = select(Report).where(Report.created_by_officer_id == current_user.id)
        
        # Count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Fetch
        skip = (page - 1) * size
        fetch_query = base_query.order_by(Report.created_at.desc()).offset(skip).limit(size)
        result = await db.execute(fetch_query)
        reports = result.scalars().all()
        
        return ReportListResponse(
            data=[ReportResponse.model_validate(r) for r in reports],
            total=total,
            page=page,
            size=size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reports: {str(e)}"
        )

@router.get(
    "/{report_id}",
    response_model=ReportDetailResponse,
    summary="Get Report Details",
    description="Retrieves specific report metadata and structured summary data (JSON)."
)
async def get_report_details(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Officer = Depends(get_current_officer)
):
    try:
        query = select(Report).where(
            Report.id == report_id,
            Report.created_by_officer_id == current_user.id
        )
        result = await db.execute(query)
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
            
        # Normally we would generate/fetch the actual data here based on `report.parameters_json`
        mock_data = {"note": "Report JSON data would be aggregated here based on parameters"}
        
        response = ReportDetailResponse.model_validate(report)
        response.report_data = mock_data
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch report details: {str(e)}"
        )
