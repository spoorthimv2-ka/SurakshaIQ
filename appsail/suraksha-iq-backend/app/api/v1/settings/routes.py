from fastapi import Request, APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any, List

from app.api.deps import get_current_officer, RequirePermission
from app.models.enums import Permission
from app.services.settings_service import SettingsService
from app.schemas.settings import (
    UserSettings,
    SystemSettings,
    Notification,
    NotificationSummary,
    ExportRequest,
    ExportResponse,
    AIReportRequest,
    AIReportResponse,
)

router = APIRouter()


@router.get(
    "/user",
    response_model=UserSettings,
    summary="Get User Settings",
    description="Retrieves settings for the current user.",
)
async def get_user_settings(
    request: Request,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_SETTINGS])),
):
    try:
        service = SettingsService(request)
        settings = await service.get_user_settings(current_officer)
        return settings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch user settings: {str(e)}")


@router.put(
    "/user",
    response_model=UserSettings,
    summary="Update User Settings",
    description="Updates settings for the current user.",
)
async def update_user_settings(
    request: Request,
    data: Dict[str, Any],
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_SETTINGS])),
):
    try:
        service = SettingsService(request)
        settings = await service.update_user_settings(current_officer, data)
        return settings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update user settings: {str(e)}")


@router.get(
    "/system",
    response_model=List[SystemSettings],
    summary="Get System Settings",
    description="Retrieves system-wide settings (admin only).",
)
async def get_system_settings(
    request: Request,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_SETTINGS])),
):
    try:
        service = SettingsService(request)
        settings = await service.get_system_settings()
        return settings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch system settings: {str(e)}")


@router.get(
    "/notifications",
    response_model=List[Notification],
    summary="Get Notifications",
    description="Retrieves notifications for the current user.",
)
async def get_notifications(
    request: Request,
    unread_only: bool = Query(False),
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_SETTINGS])),
):
    try:
        service = SettingsService(request)
        notifications = await service.get_notifications(current_officer, unread_only=unread_only)
        return notifications
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch notifications: {str(e)}")


@router.get(
    "/notifications/summary",
    response_model=NotificationSummary,
    summary="Get Notification Summary",
    description="Retrieves notification summary for the current user.",
)
async def get_notification_summary(
    request: Request,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_SETTINGS])),
):
    try:
        service = SettingsService(request)
        summary = await service.get_notification_summary(current_officer)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch notification summary: {str(e)}")


@router.patch(
    "/notifications/{notification_id}/read",
    summary="Mark Notification as Read",
    description="Marks a notification as read.",
)
async def mark_notification_read(
    request: Request,
    notification_id: str,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_SETTINGS])),
):
    try:
        service = SettingsService(request)
        result = await service.mark_notification_read(current_officer, notification_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to mark notification as read: {str(e)}")


@router.patch(
    "/notifications/{notification_id}/dismiss",
    summary="Dismiss Notification",
    description="Dismisses a notification.",
)
async def dismiss_notification(
    request: Request,
    notification_id: str,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_SETTINGS])),
):
    try:
        service = SettingsService(request)
        result = await service.dismiss_notification(current_officer, notification_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to dismiss notification: {str(e)}")


@router.post(
    "/notifications/clear-all",
    summary="Clear All Notifications",
    description="Dismisses all notifications for the current user.",
)
async def clear_all_notifications(
    request: Request,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_SETTINGS])),
):
    try:
        service = SettingsService(request)
        result = await service.clear_all_notifications(current_officer)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to clear notifications: {str(e)}")


@router.post(
    "/export",
    response_model=ExportResponse,
    summary="Export Data",
    description="Exports data in CSV, JSON, or print-friendly format.",
)
async def export_data(
    request: Request,
    export_request: ExportRequest,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_SETTINGS])),
):
    try:
        service = SettingsService(request)
        result = await service.export_data(current_officer, export_request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to export data: {str(e)}")


@router.post(
    "/reports/ai-generate",
    response_model=AIReportResponse,
    summary="AI Report Generator",
    description="Generates an AI-powered report with fallback when AI is unavailable.",
)
async def generate_ai_report(
    request: Request,
    report_request: AIReportRequest,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_SETTINGS])),
):
    try:
        service = SettingsService(request)
        result = await service.generate_ai_report(current_officer, report_request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate AI report: {str(e)}")
