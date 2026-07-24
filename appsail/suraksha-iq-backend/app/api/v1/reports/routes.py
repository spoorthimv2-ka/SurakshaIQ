from fastapi import APIRouter, Depends, Query, HTTPException, Request, status
from typing import Optional, Dict, Any, List

from app.api.deps import get_current_officer
from app.repositories.report_repo import ReportRepository
from app.services.report_service import ReportService
from app.schemas.report import ReportResponse, ReportSummaryResponse, ReportStatistics, ReportTypeInfo, ReportRequest
from app.core.logger import logger

router = APIRouter()


@router.get(
    "/",
    response_model=List[ReportResponse],
    summary="Get Reports",
    description="Retrieves a paginated list of reports."
)
async def get_reports(
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves reports from Catalyst Data Store."""
    try:
        offset = (page - 1) * size
        service = ReportService(request, ReportRepository(request))
        reports = await service.get_reports(limit=size, offset=offset)
        return [ReportResponse.model_validate(r) for r in reports]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reports: {str(e)}"
        )


@router.get(
    "/summary",
    response_model=ReportSummaryResponse,
    summary="Get Report Summary",
    description="Retrieves report summary counts."
)
async def get_report_summary(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves report summary from Catalyst Data Store."""
    try:
        service = ReportService(request, ReportRepository(request))
        summary = await service.get_summary()
        return ReportSummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch report summary: {str(e)}"
        )


@router.get(
    "/types",
    response_model=List[ReportTypeInfo],
    summary="Get Report Types",
    description="Retrieves available report types."
)
async def get_report_types(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves available report types."""
    try:
        service = ReportService(request, ReportRepository(request))
        types = await service.get_report_types()
        return [ReportTypeInfo(**t) for t in types]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch report types: {str(e)}"
        )


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    summary="Get Report Details",
    description="Retrieves specific report metadata."
)
async def get_report_details(
    request: Request,
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves report details from Catalyst Data Store."""
    try:
        service = ReportService(request, ReportRepository(request))
        report = await service.get_report(report_id)

        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

        return ReportResponse.model_validate(report)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch report details: {str(e)}"
        )


@router.post(
    "/generate",
    summary="Generate Report",
    description="Generates a new report from existing data."
)
async def generate_report(
    request: Request,
    report_request: ReportRequest,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Generates a new report deterministically from existing data."""
    try:
        officer_id = current_user.get("ROWID", current_user.get("id", ""))
        service = ReportService(request, ReportRepository(request))
        result = await service.generate_report(
            report_type=report_request.report_type.value,
            officer_id=officer_id,
            parameters={"name": report_request.name, **(report_request.parameters_json or {})},
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.delete(
    "/{report_id}",
    summary="Delete Report",
    description="Deletes a report."
)
async def delete_report(
    request: Request,
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Deletes a report from Catalyst Data Store."""
    try:
        service = ReportService(request, ReportRepository(request))
        result = await service.delete_report(report_id)
        return {"message": "Report deleted successfully", "success": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete report: {str(e)}"
        )
