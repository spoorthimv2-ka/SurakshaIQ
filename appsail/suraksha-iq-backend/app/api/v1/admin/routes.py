from fastapi import APIRouter, Depends, Query, HTTPException, Request, status as http_status
from typing import Optional, Dict, Any, List

from app.api.deps import RequirePermission
from app.models.enums import Permission
from app.services.admin_service import AdminService
from app.repositories.admin_repo import AdminRepository
from app.schemas.admin import AdminUserCreate, AdminUserUpdate, RoleInfo, AdminStatistics, AuditLog

router = APIRouter()


@router.get(
    "/users",
    response_model=List[Dict[str, Any]],
    summary="Get Users",
    description="Retrieves a paginated list of users with merged officer profiles."
)
async def get_users(
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_USER_MANAGEMENT])),
):
    """Retrieves users from Catalyst Data Store."""
    try:
        offset = (page - 1) * size
        service = AdminService(request, AdminRepository(request))
        users = await service.get_users(limit=size, offset=offset, role=role, status=status)
        return users
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )


@router.get(
    "/users/{user_id}",
    response_model=Dict[str, Any],
    summary="Get User Details",
    description="Retrieves a single user with merged officer profile."
)
async def get_user(
    request: Request,
    user_id: str,
    current_user: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_USER_MANAGEMENT])),
):
    """Retrieves user details from Catalyst Data Store."""
    try:
        service = AdminService(request, AdminRepository(request))
        user = await service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user: {str(e)}"
        )


@router.post(
    "/users",
    response_model=Dict[str, Any],
    summary="Create User",
    description="Creates a new user with optional officer profile."
)
async def create_user(
    request: Request,
    user_data: AdminUserCreate,
    current_user: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_USER_MANAGEMENT])),
):
    """Creates a new user."""
    try:
        service = AdminService(request, AdminRepository(request))
        result = await service.create_user(user_data.model_dump())
        await service.create_audit_log(
            action="CREATE_USER",
            user_id=current_user.get("email", current_user.get("user_id", "")),
            target=result.get("user_id", ""),
            metadata={"email": user_data.email, "role": user_data.role.value},
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.put(
    "/users/{user_id}",
    response_model=Dict[str, Any],
    summary="Update User",
    description="Updates an existing user."
)
async def update_user(
    request: Request,
    user_id: str,
    user_data: AdminUserUpdate,
    current_user: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_USER_MANAGEMENT])),
):
    """Updates a user."""
    try:
        service = AdminService(request, AdminRepository(request))
        result = await service.update_user(user_id, user_data.model_dump(exclude_none=True))
        await service.create_audit_log(
            action="UPDATE_USER",
            user_id=current_user.get("email", current_user.get("user_id", "")),
            target=user_id,
            metadata=user_data.model_dump(exclude_none=True),
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.delete(
    "/users/{user_id}",
    summary="Delete User",
    description="Deletes a user."
)
async def delete_user(
    request: Request,
    user_id: str,
    current_user: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_USER_MANAGEMENT])),
):
    """Deletes a user."""
    try:
        service = AdminService(request, AdminRepository(request))
        result = await service.delete_user(user_id)
        await service.create_audit_log(
            action="DELETE_USER",
            user_id=current_user.get("email", current_user.get("user_id", "")),
            target=user_id,
            metadata={},
        )
        return {"message": "User deleted successfully", "success": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


@router.patch(
    "/users/{user_id}/activate",
    response_model=Dict[str, Any],
    summary="Activate User",
    description="Activates a user account."
)
async def activate_user(
    request: Request,
    user_id: str,
    current_user: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_USER_MANAGEMENT])),
):
    """Activates a user."""
    try:
        service = AdminService(request, AdminRepository(request))
        result = await service.activate_user(user_id)
        await service.create_audit_log(
            action="ACTIVATE_USER",
            user_id=current_user.get("email", current_user.get("user_id", "")),
            target=user_id,
            metadata={},
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate user: {str(e)}"
        )


@router.patch(
    "/users/{user_id}/deactivate",
    response_model=Dict[str, Any],
    summary="Deactivate User",
    description="Deactivates a user account."
)
async def deactivate_user(
    request: Request,
    user_id: str,
    current_user: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_USER_MANAGEMENT])),
):
    """Deactivates a user."""
    try:
        service = AdminService(request, AdminRepository(request))
        result = await service.deactivate_user(user_id)
        await service.create_audit_log(
            action="DEACTIVATE_USER",
            user_id=current_user.get("email", current_user.get("user_id", "")),
            target=user_id,
            metadata={},
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate user: {str(e)}"
        )


@router.get(
    "/roles",
    response_model=List[RoleInfo],
    summary="Get Roles",
    description="Retrieves available system roles."
)
async def get_roles(
    request: Request,
    current_user: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_ROLE_ASSIGNMENT])),
):
    """Retrieves available roles."""
    try:
        service = AdminService(request, AdminRepository(request))
        roles = await service.get_roles()
        return [RoleInfo(**r) for r in roles]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch roles: {str(e)}"
        )


@router.get(
    "/officers",
    summary="Get Officers",
    description="Retrieves officers with district and station details.",
)
async def get_officers(
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    station_id: Optional[str] = Query(None),
    district_id: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_USER_MANAGEMENT])),
):
    try:
        offset = (page - 1) * size
        service = AdminService(request, AdminRepository(request))
        officers = await service.list_officers(limit=size, offset=offset, station_id=station_id, district_id=district_id)
        return officers
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch officers: {str(e)}"
        )


@router.get(
    "/districts",
    summary="Get Districts",
    description="Retrieves districts with station and officer counts.",
)
async def get_districts(
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_USER_MANAGEMENT])),
):
    try:
        offset = (page - 1) * size
        service = AdminService(request, AdminRepository(request))
        districts = await service.list_districts(limit=size, offset=offset)
        return districts
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch districts: {str(e)}"
        )


@router.get(
    "/police-stations",
    summary="Get Police Stations",
    description="Retrieves police stations with district and officer details.",
)
async def get_police_stations(
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    district_id: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_USER_MANAGEMENT])),
):
    try:
        offset = (page - 1) * size
        service = AdminService(request, AdminRepository(request))
        stations = await service.list_police_stations(limit=size, offset=offset, district_id=district_id)
        return stations
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch police stations: {str(e)}"
        )


@router.get(
    "/statistics",
    response_model=AdminStatistics,
    summary="Get Admin Statistics",
    description="Retrieves aggregated admin statistics."
)
async def get_statistics(
    request: Request,
    current_user: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_USER_MANAGEMENT])),
):
    """Retrieves admin statistics."""
    try:
        service = AdminService(request, AdminRepository(request))
        stats = await service.get_statistics()
        return AdminStatistics(**stats)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch statistics: {str(e)}"
        )


@router.get(
    "/audit-logs",
    response_model=List[AuditLog],
    summary="Get Audit Logs",
    description="Retrieves audit log entries."
)
async def get_audit_logs(
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_USER_MANAGEMENT])),
):
    """Retrieves audit logs."""
    try:
        offset = (page - 1) * size
        service = AdminService(request, AdminRepository(request))
        logs = await service.get_audit_logs(limit=size, offset=offset)
        return [AuditLog(**log) for log in logs]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch audit logs: {str(e)}"
        )
