from fastapi import Request,  APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any, List

from app.api.deps import get_current_officer
from app.repositories.district_repo import DistrictRepository
from app.services.dashboard_service import DashboardService
from app.schemas.district import DistrictResponse, DistrictSummary
from app.schemas.district_analytics import DistrictRollupResponse, DistrictTrend
from app.models.enums import Role

router = APIRouter()


def _to_district_summary(district: Dict[str, Any], case_count: int = 0, risk_index: float = 0.0) -> Dict[str, Any]:
    return {
        "id": district.get("ROWID", ""),
        "name": district.get("name", "Unknown"),
        "caseCount": case_count,
        "riskIndex": risk_index,
    }


@router.get(
    "/",
    response_model=List[DistrictSummary],
    summary="Get Districts",
    description="Retrieves all registered districts.",
)
async def get_districts(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_officer)
):
    """Retrieves all districts from Catalyst Data Store."""
    try:
        repo = DistrictRepository(request)
        districts = await repo.find_active(limit=10000)
        summary = DashboardService(request)
        stats = await summary.get_district_summary(current_user)
        stats_map = {s.district_id: s for s in stats}
        result: List[Dict[str, Any]] = []
        for d in districts:
            stats_row = stats_map.get(d.get("ROWID", ""))
            result.append(_to_district_summary(
                d,
                case_count=(stats_row.crime_count + stats_row.fir_count) if stats_row else 0,
                risk_index=0.0,
            ))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch districts: {str(e)}"
        )


@router.get(
    "/{district_id}",
    response_model=DistrictSummary,
    summary="Get District By ID",
    description="Retrieves a single district by its ROWID.",
)
async def get_district(
    request: Request,
    district_id: str,
    current_user: Dict[str, Any] = Depends(get_current_officer)
):
    """Retrieves a district by ROWID."""
    try:
        repo = DistrictRepository(request)
        district = await repo.find_by_id(district_id)
        if not district:
            raise HTTPException(status_code=404, detail="District not found")
        service = DashboardService(request)
        stats = await service.get_district_summary(current_user)
        stats_row = next((s for s in stats if s.district_id == district_id), None)
        return _to_district_summary(
            district,
            case_count=(stats_row.crime_count + stats_row.fir_count) if stats_row else 0,
            risk_index=0.0,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch district: {str(e)}"
        )


@router.get(
    "/{district_id}/analytics",
    response_model=DistrictRollupResponse,
    summary="Get District Analytics",
    description="Retrieves district-level rollups and comparisons (if officer roles permit)."
)
async def get_district_analytics(
    request: Request,
    district_id: str,
    start_date: Optional[str] = Query(None, description="Start date (UTC)"),
    end_date: Optional[str] = Query(None, description="End date (UTC)"),
    current_user: Dict[str, Any] = Depends(get_current_officer)
):
    """Retrieves district analytics from Catalyst Data Store."""
    try:
        district_repo = DistrictRepository(request)
        district = await district_repo.find_by_id(district_id)
        if not district:
            raise HTTPException(status_code=404, detail="District not found")

        service = DashboardService(request)
        stats = await service.get_statistics(current_user)

        total_crimes = 0
        for ds in stats.by_district:
            if ds.district_id == district_id:
                total_crimes = ds.count
                break

        comparisons = None
        officer_role = current_user.get("role", "")
        state_roles = [Role.STATE_COMMAND.value, Role.SYSTEM_ADMINISTRATOR.value, Role.CID_ANALYST.value, Role.RANGE_IG.value]
        if officer_role in state_roles:
            comparisons = []
            for ds in stats.by_district:
                if ds.district_id != district_id:
                    comparisons.append(DistrictTrend(
                        district_id=ds.district_id,
                        district_name=ds.district_name,
                        current_count=ds.count,
                        trend_direction="FLAT",
                        trend_percentage=0.0
                    ))

        return DistrictRollupResponse(
            district_id=district_id,
            district_name=district.get("name", "Unknown"),
            total_crimes=total_crimes,
            comparisons=comparisons
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch district analytics: {str(e)}"
        )
