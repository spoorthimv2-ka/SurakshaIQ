from fastapi import APIRouter, Depends, Query, HTTPException, Request, status
from typing import Optional, Dict, Any, List

from app.api.deps import get_current_officer
from app.services.search_service import SearchService
from app.repositories.search_repo import SearchRepository
from app.schemas.search import SearchResponse, SearchSuggestion, SearchFilters

router = APIRouter()


@router.get(
    "/",
    response_model=SearchResponse,
    summary="Global Search",
    description="Searches across crimes, FIRs, hotspots, repeat offenders, network entities, predictive risk, anomalies, alerts, and reports."
)
async def global_search(
    request: Request,
    keyword: str = Query(..., min_length=1, description="Search keyword"),
    category: Optional[str] = Query(None, description="Filter by category"),
    district: Optional[str] = Query(None, description="Filter by district ID"),
    station: Optional[str] = Query(None, description="Filter by station ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Performs global search across all entities."""
    try:
        service = SearchService(request, SearchRepository(request))
        result = await service.search(
            keyword=keyword,
            category=category,
            district_id=district,
            station_id=station,
            limit=limit,
            offset=offset,
        )
        return SearchResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform search: {str(e)}"
        )


@router.get(
    "/suggestions",
    response_model=List[SearchSuggestion],
    summary="Search Suggestions",
    description="Returns top matching keywords for autocomplete."
)
async def search_suggestions(
    request: Request,
    keyword: str = Query(..., min_length=1, description="Partial keyword"),
    limit: int = Query(10, ge=1, le=10),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Returns search suggestions."""
    try:
        service = SearchService(request, SearchRepository(request))
        suggestions = await service.get_suggestions(keyword=keyword, limit=limit)
        return [SearchSuggestion(**s) for s in suggestions]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch suggestions: {str(e)}"
        )


@router.get(
    "/filters",
    response_model=SearchFilters,
    summary="Search Filters",
    description="Returns available filter options for global search."
)
async def search_filters(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Returns available search filters."""
    try:
        service = SearchService(request, SearchRepository(request))
        filters = await service.get_filters()
        return SearchFilters(**filters)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch search filters: {str(e)}"
        )
