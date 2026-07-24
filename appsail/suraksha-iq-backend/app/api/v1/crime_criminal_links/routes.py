from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any, List

from app.api.deps import get_current_officer
from app.repositories.crime_criminal_link_repo import CrimeCriminalLinkRepository
from app.schemas.crime_criminal_link import (
    CrimeCriminalLinkCreate,
    CrimeCriminalLinkUpdate,
    CrimeCriminalLinkResponse,
)
from app.core.exceptions import DataValidationError, RepositoryError

router = APIRouter()


@router.post(
    "/",
    response_model=CrimeCriminalLinkResponse,
    summary="Create Crime-Criminal Link",
    description="Explicitly links a criminal to a crime. Replaces district-proximity inference.",
    status_code=status.HTTP_201_CREATED,
)
async def create_link(
    payload: CrimeCriminalLinkCreate,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    try:
        repo = CrimeCriminalLinkRepository(None)
        repo.request = current_user.get("request")
        result = await repo.create_link(
            crime_id=payload.crime_id,
            criminal_id=payload.criminal_id,
            role=payload.role,
            linked_by_officer_id=current_user.get("ROWID", ""),
            notes=payload.notes or "",
        )
        return CrimeCriminalLinkResponse(
            ROWID=result.get("ROWID", ""),
            crime_id=payload.crime_id,
            criminal_id=payload.criminal_id,
            role=payload.role,
            notes=payload.notes,
            linked_by_officer_id=current_user.get("ROWID", ""),
            linked_at=result.get("linked_at"),
            CREATEDTIME=result.get("CREATEDTIME", ""),
            MODIFIEDTIME=result.get("MODIFIEDTIME", ""),
        )
    except HTTPException:
        raise
    except DataValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RepositoryError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create link: {str(e)}",
        )


@router.get(
    "/crime/{crime_id}",
    response_model=List[CrimeCriminalLinkResponse],
    summary="List Links for a Crime",
    description="Retrieves all criminals linked to a specific crime.",
)
async def list_by_crime(
    crime_id: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    try:
        repo = CrimeCriminalLinkRepository(None)
        repo.request = current_user.get("request")
        links = await repo.find_by_crime(crime_id, limit=limit, offset=offset)
        return [CrimeCriminalLinkResponse(**link) for link in links]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch crime links: {str(e)}",
        )


@router.get(
    "/criminal/{criminal_id}",
    response_model=List[CrimeCriminalLinkResponse],
    summary="List Links for a Criminal",
    description="Retrieves all crimes linked to a specific criminal.",
)
async def list_by_criminal(
    criminal_id: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    try:
        repo = CrimeCriminalLinkRepository(None)
        repo.request = current_user.get("request")
        links = await repo.find_by_criminal(criminal_id, limit=limit, offset=offset)
        return [CrimeCriminalLinkResponse(**link) for link in links]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch criminal links: {str(e)}",
        )


@router.delete(
    "/{link_id}",
    summary="Delete Crime-Criminal Link",
    description="Removes an explicit crime-criminal link.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_link(
    link_id: str,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    try:
        repo = CrimeCriminalLinkRepository(None)
        repo.request = current_user.get("request")
        await repo.delete_link(link_id)
        return None
    except HTTPException:
        raise
    except DataValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RepositoryError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete link: {str(e)}",
        )
