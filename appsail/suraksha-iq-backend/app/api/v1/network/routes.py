from fastapi import Request,  APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any, List

from app.api.deps import get_current_officer
from app.services.network_service import NetworkService
from app.schemas.network import NetworkGraphResponse, NetworkStatistics, NetworkSearchResponse

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
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves network graph from Catalyst Data Store."""
    try:
        service = NetworkService(request)
        graph = await service.get_network(current_user, limit=limit)
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
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves network statistics from Catalyst Data Store."""
    try:
        service = NetworkService(request)
        stats = await service.get_statistics(current_user)
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
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves offender network from Catalyst Data Store."""
    try:
        service = NetworkService(request)
        graph = await service.get_offender_network(current_user, offender_id)
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
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves station network from Catalyst Data Store."""
    try:
        service = NetworkService(request)
        graph = await service.get_station_network(current_user, station_id)
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
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves district network from Catalyst Data Store."""
    try:
        service = NetworkService(request)
        graph = await service.get_district_network(current_user, district_id)
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
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Searches the network graph from Catalyst Data Store."""
    try:
        service = NetworkService(request)
        result = await service.search(current_user, query=q, limit=limit)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search network: {str(e)}"
        )
