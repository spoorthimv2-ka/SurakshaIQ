from fastapi import Request,  APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any, List

from app.api.deps import get_current_officer, RequirePermission
from app.models.enums import Permission
from app.services.network_service import NetworkService
from app.schemas.network import (
    NetworkGraphResponse,
    NetworkStatistics,
    NetworkSearchResponse,
    NetworkFilters,
    AdvancedGraphResponse,
    NetworkAnalyticsResponse,
    NetworkTimelineResponse,
    CommunityDetectionResponse,
    CentralActorResponse,
)

router = APIRouter()


@router.get(
    "/",
    response_model=NetworkGraphResponse,
    summary="Get Network Graph",
    description="Retrieves the full relationship network graph from Catalyst Data Store.",
)
async def get_network(
    request: Request,
    limit: int = Query(500, ge=1, le=2000),
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_NETWORK_ANALYSIS])),
):
    """Retrieves network graph from Catalyst Data Store."""
    try:
        service = NetworkService(request)
        graph = await service.get_network(current_officer, limit=limit)
        return graph
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch network: {str(e)}"
        )


@router.get(
    "/statistics",
    response_model=NetworkStatistics,
    summary="Get Network Statistics",
    description="Retrieves aggregated statistics for the network graph.",
)
async def get_network_statistics(
    request: Request,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_NETWORK_ANALYSIS])),
):
    """Retrieves network statistics from Catalyst Data Store."""
    try:
        service = NetworkService(request)
        stats = await service.get_statistics(current_officer)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch network statistics: {str(e)}"
        )


@router.get(
    "/offenders/{offender_id}",
    response_model=NetworkGraphResponse,
    summary="Get Offender Network",
    description="Retrieves the relationship subgraph for a specific offender.",
)
async def get_offender_network(
    request: Request,
    offender_id: str,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_NETWORK_ANALYSIS])),
):
    """Retrieves offender network from Catalyst Data Store."""
    try:
        service = NetworkService(request)
        graph = await service.get_offender_network(current_officer, offender_id)
        return graph
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch offender network: {str(e)}"
        )


@router.get(
    "/stations/{station_id}",
    response_model=NetworkGraphResponse,
    summary="Get Station Network",
    description="Retrieves the relationship subgraph for a specific police station.",
)
async def get_station_network(
    request: Request,
    station_id: str,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_NETWORK_ANALYSIS])),
):
    """Retrieves station network from Catalyst Data Store."""
    try:
        service = NetworkService(request)
        graph = await service.get_station_network(current_officer, station_id)
        return graph
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch station network: {str(e)}"
        )


@router.get(
    "/districts/{district_id}",
    response_model=NetworkGraphResponse,
    summary="Get District Network",
    description="Retrieves the relationship subgraph for a specific district.",
)
async def get_district_network(
    request: Request,
    district_id: str,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_NETWORK_ANALYSIS])),
):
    """Retrieves district network from Catalyst Data Store."""
    try:
        service = NetworkService(request)
        graph = await service.get_district_network(current_officer, district_id)
        return graph
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch district network: {str(e)}"
        )


@router.get(
    "/search",
    response_model=NetworkSearchResponse,
    summary="Search Network",
    description="Searches the network graph by query string.",
)
async def search_network(
    request: Request,
    q: str = Query(..., description="Search query"),
    limit: int = Query(50, ge=1, le=200),
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_NETWORK_ANALYSIS])),
):
    """Searches the network graph from Catalyst Data Store."""
    try:
        service = NetworkService(request)
        result = await service.search(current_officer, query=q, limit=limit)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search network: {str(e)}"
        )


@router.get(
    "/advanced",
    response_model=AdvancedGraphResponse,
    summary="Get Advanced Network Graph",
    description="Retrieves advanced network graph with communities, centrality, and richer relationships.",
)
async def get_advanced_graph(
    request: Request,
    crime_category: Optional[str] = Query(None, description="Filter by crime category"),
    district_id: Optional[str] = Query(None, description="Filter by district ID"),
    station_id: Optional[str] = Query(None, description="Filter by station ID"),
    relationship_type: Optional[str] = Query(None, description="Filter by relationship type"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    active_investigations: Optional[bool] = Query(None, description="Filter active investigations"),
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_NETWORK_ANALYSIS])),
):
    """Retrieves advanced network graph from Catalyst Data Store."""
    try:
        service = NetworkService(request)
        filters = {
            "crime_category": crime_category,
            "district_id": district_id,
            "station_id": station_id,
            "relationship_type": relationship_type,
            "risk_level": risk_level,
            "active_investigations": active_investigations,
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        graph = await service.get_advanced_graph(current_officer, filters=filters)
        return graph
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch advanced network: {str(e)}"
        )


@router.get(
    "/analytics",
    response_model=NetworkAnalyticsResponse,
    summary="Get Network Analytics",
    description="Retrieves network analytics including community stats, central actors, bridge nodes.",
)
async def get_network_analytics(
    request: Request,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_NETWORK_ANALYSIS])),
):
    """Retrieves network analytics."""
    try:
        service = NetworkService(request)
        result = await service.get_analytics(current_officer)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch network analytics: {str(e)}"
        )


@router.get(
    "/timeline",
    response_model=NetworkTimelineResponse,
    summary="Get Network Timeline",
    description="Retrieves network evolution timeline based on crime dates.",
)
async def get_network_timeline(
    request: Request,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_NETWORK_ANALYSIS])),
):
    """Retrieves network timeline."""
    try:
        service = NetworkService(request)
        result = await service.get_timeline(current_officer)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch network timeline: {str(e)}"
        )


@router.get(
    "/communities",
    response_model=CommunityDetectionResponse,
    summary="Get Community Detection",
    description="Retrieves detected communities in the network graph.",
)
async def get_communities(
    request: Request,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_NETWORK_ANALYSIS])),
):
    """Retrieves community detection results."""
    try:
        service = NetworkService(request)
        result = await service.get_communities(current_officer)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch communities: {str(e)}"
        )


@router.get(
    "/central-actors",
    response_model=CentralActorResponse,
    summary="Get Central Actors",
    description="Retrieves central actors by requested metric (degree/betweenness).",
)
async def get_central_actors(
    request: Request,
    metric: str = Query("degree", description="Centrality metric"),
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_NETWORK_ANALYSIS])),
):
    """Retrieves central actors."""
    try:
        service = NetworkService(request)
        result = await service.get_central_actors(current_officer, metric=metric)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch central actors: {str(e)}"
        )


@router.get(
    "/bridge-nodes",
    summary="Get Bridge Nodes",
    description="Retrieves bridge nodes connecting different communities.",
)
async def get_bridge_nodes(
    request: Request,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_NETWORK_ANALYSIS])),
):
    """Retrieves bridge nodes."""
    try:
        service = NetworkService(request)
        result = await service.get_bridge_nodes(current_officer)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch bridge nodes: {str(e)}"
        )


@router.get(
    "/search/advanced",
    response_model=NetworkSearchResponse,
    summary="Advanced Network Search",
    description="Search across offenders, FIRs, vehicles, phones, addresses, and aliases.",
)
async def advanced_search_network(
    request: Request,
    q: str = Query(..., description="Search query"),
    limit: int = Query(50, ge=1, le=200),
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_NETWORK_ANALYSIS])),
):
    """Advanced network search."""
    try:
        service = NetworkService(request)
        result = await service.advanced_search(current_officer, query=q, limit=limit)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform advanced search: {str(e)}"
        )
