from fastapi import Request,  APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any, List

from app.api.deps import get_current_officer
from app.repositories.crime_repo import CrimeRepository
from app.services.crime_service import CrimeService
from app.schemas.crime import CrimeCreate, CrimeUpdate, CrimeResponse
from app.core.exceptions import DataValidationError, RepositoryError
from app.core.logger import logger

router = APIRouter()


@router.get(
    "/",
    response_model=List[CrimeResponse],
    summary="Get Crimes",
    description="Retrieves a paginated list of crimes with optional filters.",
)
async def get_crimes(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    keyword: Optional[str] = Query(None, description="Search keyword across title, description, or crime type"),
    district_id: Optional[str] = Query(None, description="Filter by district ID"),
    station_id: Optional[str] = Query(None, description="Filter by police station ID"),
    crime_type: Optional[str] = Query(None, description="Filter by crime type"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    date_from: Optional[str] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves crimes with optional filters."""
    try:
        repo = CrimeRepository(request)
        service = CrimeService(request, repo)

        crimes = await service.find_all_with_filters(
            limit=limit,
            offset=offset,
            keyword=keyword,
            district_id=district_id,
            station_id=station_id,
            crime_type=crime_type,
            status=status_filter,
            date_from=date_from,
            date_to=date_to,
        )
        return [CrimeResponse.model_validate(c) for c in crimes]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch crimes: {str(e)}",
        )


@router.get(
    "/{crime_id}",
    response_model=CrimeResponse,
    summary="Get Crime by ID",
    description="Retrieves a single crime by its ROWID.",
)
async def get_crime(
    request: Request,
    crime_id: str,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves a Crime by ID."""
    try:
        repo = CrimeRepository(request)
        service = CrimeService(request, repo)

        crime = await service.get_by_id(crime_id)
        if not crime:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crime not found")

        logger.info("Crime Retrieved")
        return CrimeResponse.model_validate(crime)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch crime: {str(e)}",
        )


@router.post(
    "/",
    response_model=CrimeResponse,
    summary="Create Crime",
    description="Creates a new crime record.",
    status_code=status.HTTP_201_CREATED,
)
async def create_crime(
    request: Request,
    payload: CrimeCreate,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Creates a new Crime."""
    try:
        repo = CrimeRepository(request)
        service = CrimeService(request, repo)

        result = await service.create(payload.model_dump())
        return CrimeResponse.model_validate(result)
    except HTTPException:
        raise
    except DataValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RepositoryError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create crime: {str(e)}",
        )


@router.put(
    "/{crime_id}",
    response_model=CrimeResponse,
    summary="Update Crime",
    description="Updates an existing crime record.",
)
async def update_crime(
    request: Request,
    crime_id: str,
    payload: CrimeUpdate,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Updates an existing Crime."""
    try:
        repo = CrimeRepository(request)
        service = CrimeService(request, repo)

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No update data provided")

        result = await service.update(crime_id, update_data)
        return CrimeResponse.model_validate(result)
    except HTTPException:
        raise
    except DataValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RepositoryError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update crime: {str(e)}",
        )


@router.delete(
    "/{crime_id}",
    summary="Delete Crime",
    description="Deletes a crime record.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_crime(
    request: Request,
    crime_id: str,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Deletes a Crime."""
    try:
        repo = CrimeRepository(request)
        service = CrimeService(request, repo)

        await service.delete(crime_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete crime: {str(e)}",
        )
