from fastapi import Request,  APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any

from app.api.deps import get_current_officer
from app.repositories.district_repo import DistrictRepository
from app.services.dashboard_service import DashboardService
from app.schemas.district_analytics import DistrictRollupResponse, DistrictTrend
from app.models.enums import Role

router = APIRouter()

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
