from fastapi import APIRouter, Depends, Query, HTTPException, status
from neo4j import AsyncSession
from typing import Optional

from app.database.neo4j.connection import get_neo4j_session
from app.models.officer import Officer
from app.api.deps import get_current_officer
from app.schemas.risk import RiskScoreResponse
from app.graph.link_analysis.offender_graph_repo import OffenderGraphRepository
from app.analytics.prediction.risk_model import calculate_offender_risk

router = APIRouter()

@router.get(
    "/offender/{offender_id}",
    response_model=RiskScoreResponse,
    summary="Get Offender Risk Score",
    description="Calculates a risk score for a specific offender based on graph history."
)
async def get_offender_risk(
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
                detail="Offender not found in graph database"
            )
            
        risk_score = calculate_offender_risk(offender)
        return risk_score
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate risk score: {str(e)}"
        )
