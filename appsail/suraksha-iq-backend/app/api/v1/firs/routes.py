from fastapi import Request,  APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any, List

from app.api.deps import get_current_officer
from app.repositories.fir_repo import FIRRepository
from app.services.fir_service import FIRService
from app.schemas.fir import FIRCreate, FIRUpdate, FIRResponse
from app.core.exceptions import DataValidationError, RepositoryError
from app.core.logger import logger

router = APIRouter()


@router.get(
    "/",
    response_model=List[FIRResponse],
    summary="Get FIRs",
    description="Retrieves a paginated list of FIRs with optional filters.",
)
async def get_firs(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    fir_number: Optional[str] = Query(None, description="Search by FIR number"),
    district_id: Optional[str] = Query(None, description="Filter by district ID"),
    station_id: Optional[str] = Query(None, description="Filter by police station ID"),
    officer_id: Optional[str] = Query(None, description="Filter by investigating officer ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    date_from: Optional[str] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves FIRs with optional filters."""
    try:
        repo = FIRRepository(request)
        service = FIRService(request, repo)

        firs = await service.find_all_with_filters(
            limit=limit,
            offset=offset,
            fir_number=fir_number,
            district_id=district_id,
            station_id=station_id,
            officer_id=officer_id,
            status=status_filter,
            date_from=date_from,
            date_to=date_to,
        )
        return [FIRResponse.model_validate(f) for f in firs]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch FIRs: {str(e)}",
        )


@router.get(
    "/{fir_id}",
    response_model=FIRResponse,
    summary="Get FIR by ID",
    description="Retrieves a single FIR by its ROWID.",
)
async def get_fir(
    request: Request,
    fir_id: str,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Retrieves an FIR by ID."""
    try:
        repo = FIRRepository(request)
        service = FIRService(request, repo)

        fir = await service.get_by_id(fir_id)
        if not fir:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FIR not found")

        logger.info("FIR Retrieved")
        return FIRResponse.model_validate(fir)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch FIR: {str(e)}",
        )


@router.post(
    "/",
    response_model=FIRResponse,
    summary="Create FIR",
    description="Creates a new FIR record.",
    status_code=status.HTTP_201_CREATED,
)
async def create_fir(
    request: Request,
    payload: FIRCreate,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Creates a new FIR."""
    try:
        repo = FIRRepository(request)
        service = FIRService(request, repo)

        result = await service.create(payload.model_dump())
        return FIRResponse.model_validate(result)
    except HTTPException:
        raise
    except DataValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RepositoryError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create FIR: {str(e)}",
        )


@router.put(
    "/{fir_id}",
    response_model=FIRResponse,
    summary="Update FIR",
    description="Updates an existing FIR record.",
)
async def update_fir(
    request: Request,
    fir_id: str,
    payload: FIRUpdate,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Updates an existing FIR."""
    try:
        repo = FIRRepository(request)
        service = FIRService(request, repo)

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No update data provided")

        result = await service.update(fir_id, update_data)
        return FIRResponse.model_validate(result)
    except HTTPException:
        raise
    except DataValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RepositoryError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update FIR: {str(e)}",
        )


@router.delete(
    "/{fir_id}",
    summary="Delete FIR",
    description="Deletes an FIR record.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_fir(
    request: Request,
    fir_id: str,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    """Deletes an FIR."""
    try:
        repo = FIRRepository(request)
        service = FIRService(request, repo)

        await service.delete(fir_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete FIR: {str(e)}",
        )
