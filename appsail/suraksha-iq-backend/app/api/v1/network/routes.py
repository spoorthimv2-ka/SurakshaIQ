from fastapi import APIRouter, Depends, HTTPException, status
from neo4j import AsyncSession
from typing import Optional

from app.database.neo4j.connection import get_neo4j_session
from app.models.officer import Officer
from app.api.deps import get_current_officer
from app.schemas.network import NetworkGraphResponse, Node, Link
from app.graph.link_analysis.offender_graph_repo import OffenderGraphRepository

router = APIRouter()

@router.get(
    "/offender/{offender_id}",
    response_model=NetworkGraphResponse,
    summary="Get Offender Network Graph",
    description="Retrieves a graph of relationships (crimes, co-offenders) for a specific offender suitable for D3.js visualization."
)
async def get_offender_network(
    offender_id: str,
    neo4j_session: Optional[AsyncSession] = Depends(get_neo4j_session),
    current_user: Officer = Depends(get_current_officer)
):
    try:
        repo = OffenderGraphRepository(neo4j_session)
        graph_data = await repo.get_offender_network(offender_id)
        
        # Additional centrality metrics could be calculated here or in the repo.
        # For this scaffold, we return a simple representation.
        centrality = {
            offender_id: 1.0 # placeholder
        }
        
        return NetworkGraphResponse(
            nodes=[Node.model_validate(n) for n in graph_data.get("nodes", [])],
            links=[Link.model_validate(l) for l in graph_data.get("links", [])],
            centrality_metrics=centrality
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch offender network: {str(e)}"
        )
