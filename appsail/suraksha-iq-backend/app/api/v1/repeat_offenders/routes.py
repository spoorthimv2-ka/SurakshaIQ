from fastapi import APIRouter, Depends, Query, HTTPException, status
from neo4j import AsyncSession
from typing import Optional

from app.database.neo4j.connection import get_neo4j_session
from app.models.officer import Officer
from app.api.deps import get_current_officer
from app.schemas.offender import RepeatOffenderResponse, OffenderSummary
from app.graph.link_analysis.offender_graph_repo import OffenderGraphRepository

router = APIRouter()

@router.get(
    "/",
    response_model=RepeatOffenderResponse,
    summary="Get Repeat Offenders",
    description="Retrieves a paginated list of repeat offenders based on graph analysis."
)
async def get_repeat_offenders(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    neo4j_session: Optional[AsyncSession] = Depends(get_neo4j_session),
    current_user: Officer = Depends(get_current_officer)
):
    try:
        skip = (page - 1) * size
        repo = OffenderGraphRepository(neo4j_session)
        
        # We don't apply strict jurisdiction filtering on offenders yet since 
        # graph nodes typically represent state-wide identities, but this could be
        # scoped by the crimes they are linked to if needed.
        
        offenders, total_count = await repo.get_repeat_offenders(skip=skip, limit=size)
        
        return RepeatOffenderResponse(
            data=offenders,
            total=total_count,
            page=page,
            size=size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch repeat offenders: {str(e)}"
        )

@router.get(
    "/{offender_id}",
    response_model=OffenderSummary,
    summary="Get Repeat Offender Details",
    description="Retrieves detailed graph link information for a specific repeat offender."
)
async def get_offender_details(
    offender_id: str,
    neo4j_session: Optional[AsyncSession] = Depends(get_neo4j_session),
    current_user: Officer = Depends(get_current_officer)
):
    try:
        repo = OffenderGraphRepository(neo4j_session)
        offender = await repo.get_offender_by_id(offender_id)
        
        if not offender:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offender not found"
            )
            
        return offender
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch offender details: {str(e)}"
        )
