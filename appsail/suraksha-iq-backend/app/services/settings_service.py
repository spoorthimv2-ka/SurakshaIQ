from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from fastapi import Request, APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel

from app.api.deps import get_current_officer
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError
from app.core.logger import logger
import traceback
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
from app.core.utils import catalyst_datetime


class SettingsService:
    def __init__(self, request: Request):
        self.request = request
        self.repo = BaseCatalystRepository(request, table_name="AppUser")

    async def get_user_settings(self, officer: Dict[str, Any]) -> UserSettings:
        user_id = officer.get("ROWID", officer.get("id", ""))
        try:
            user = await self.repo.find_by_id(user_id)
            if not user:
                return UserSettings(user_id=user_id)
            return UserSettings(
                user_id=user_id,
                theme=user.get("theme", "light"),
                language=user.get("language", "en"),
                notifications_enabled=user.get("notifications_enabled", True),
                email_alerts=user.get("email_alerts", True),
                push_notifications=user.get("push_notifications", True),
                ai_suggestions=user.get("ai_suggestions", True),
                default_district_id=user.get("default_district_id"),
                default_station_id=user.get("default_station_id"),
                timezone=user.get("timezone", "Asia/Kolkata"),
            )
        except Exception as e:
            logger.warning(f"Failed to load user settings: {e}")
            return UserSettings(user_id=user_id)

    async def update_user_settings(self, officer: Dict[str, Any], data: Dict[str, Any]) -> UserSettings:
        user_id = officer.get("ROWID", officer.get("id", ""))
        try:
            table = self.repo.get_table()
            row_data = {k: v for k, v in data.items() if v is not None}
            row_data["ROWID"] = user_id
            table.update_row(row_data)
            return await self.get_user_settings(officer)
        except Exception as e:
            logger.error(f"Failed to update user settings: {e}")
            raise RepositoryError(f"Failed to update settings: {e}")

    async def get_system_settings(self) -> List[SystemSettings]:
        defaults = [
            SystemSettings(key="app_name", value="SurakshaIQ", description="Application name", updated_at=datetime.now(timezone.utc).isoformat()),
            SystemSettings(key="maintenance_mode", value=False, description="Enable maintenance mode", updated_at=datetime.now(timezone.utc).isoformat()),
            SystemSettings(key="max_login_attempts", value=5, description="Maximum failed login attempts before lockout", updated_at=datetime.now(timezone.utc).isoformat()),
            SystemSettings(key="session_timeout_minutes", value=60, description="Session timeout in minutes", updated_at=datetime.now(timezone.utc).isoformat()),
            SystemSettings(key="ai_fallback_enabled", value=True, description="Enable deterministic AI fallback", updated_at=datetime.now(timezone.utc).isoformat()),
        ]
        return defaults

    async def get_notifications(self, officer: Dict[str, Any], unread_only: bool = False) -> List[Notification]:
        user_id = officer.get("ROWID", officer.get("id", ""))
        notifications: List[Notification] = []
        try:
            table = self.repo.get_table()
            result = table.get_rows()
            for item in result:
                if not isinstance(item, dict):
                    continue
                nid = item.get("ROWID", "")
                if not nid:
                    continue
                if unread_only and item.get("read", False):
                    continue
                notifications.append(Notification(
                    notification_id=str(nid),
                    user_id=item.get("user_id", user_id),
                    type=item.get("type", "system"),
                    title=item.get("title", ""),
                    message=item.get("message", ""),
                    severity=item.get("severity", "info"),
                    read=item.get("read", False),
                    dismissed=item.get("dismissed", False),
                    created_at=item.get("CREATEDTIME", datetime.now(timezone.utc).isoformat()),
                    read_at=item.get("read_at"),
                    metadata=item.get("metadata", {}),
                ))
        except Exception as exception:
            logger.warning("Failed to load notifications: %s\n%s", exception, traceback.format_exc())
        if not notifications:
            notifications = [
                Notification(
                    notification_id="sample-1",
                    user_id=user_id,
                    type="crime_alert",
                    title="New crime reported in your district",
                    message="A new theft incident was reported in Bangalore Urban district.",
                    severity="high",
                    created_at=datetime.now(timezone.utc).isoformat(),
                ),
                Notification(
                    notification_id="sample-2",
                    user_id=user_id,
                    type="ai_recommendation",
                    title="AI suggests increased patrols",
                    message="Based on recent trends, consider increasing patrols in high-risk zones.",
                    severity="medium",
                    created_at=datetime.now(timezone.utc).isoformat(),
                ),
            ]
        notifications.sort(key=lambda x: x.created_at, reverse=True)
        return notifications

    async def get_notification_summary(self, officer: Dict[str, Any]) -> NotificationSummary:
        notifications = await self.get_notifications(officer)
        unread = [n for n in notifications if not n.read]
        by_type: Dict[str, int] = {}
        by_severity: Dict[str, int] = {}
        for n in notifications:
            by_type[n.type] = by_type.get(n.type, 0) + 1
            by_severity[n.severity] = by_severity.get(n.severity, 0) + 1
        return NotificationSummary(
            total=len(notifications),
            unread=len(unread),
            by_type=by_type,
            by_severity=by_severity,
        )

    async def mark_notification_read(self, officer: Dict[str, Any], notification_id: str) -> Dict[str, Any]:
        try:
            table = self.repo.get_table()
            row = table.get_row(notification_id)
            if row:
                row["read"] = True
                row["read_at"] = catalyst_datetime()
                table.update_row(row)
            return {"success": True}
        except Exception as e:
            logger.error(f"Failed to mark notification read: {e}")
            return {"success": False}

    async def dismiss_notification(self, officer: Dict[str, Any], notification_id: str) -> Dict[str, Any]:
        try:
            table = self.repo.get_table()
            row = table.get_row(notification_id)
            if row:
                row["dismissed"] = True
                table.update_row(row)
            return {"success": True}
        except Exception as e:
            logger.error(f"Failed to dismiss notification: {e}")
            return {"success": False}

    async def clear_all_notifications(self, officer: Dict[str, Any]) -> Dict[str, Any]:
        notifications = await self.get_notifications(officer)
        try:
            table = self.repo.get_table()
            for n in notifications:
                row = table.get_row(n.notification_id)
                if row:
                    row["dismissed"] = True
                    table.update_row(row)
            return {"success": True, "cleared": len(notifications)}
        except Exception as e:
            logger.error(f"Failed to clear notifications: {e}")
            return {"success": False}

    @staticmethod
    def _generate_csv(data: List[Dict[str, Any]], headers: List[str]) -> str:
        lines = [",".join(headers)]
        for row in data:
            values = []
            for h in headers:
                val = row.get(h, "")
                if isinstance(val, str) and ("," in val or '"' in val):
                    val = '"' + val.replace('"', '""') + '"'
                values.append(str(val))
            lines.append(",".join(values))
        return "\n".join(lines)

    @staticmethod
    def _generate_json(data: Any) -> str:
        import json
        return json.dumps(data, indent=2, default=str)

    async def export_data(self, officer: Dict[str, Any], request: ExportRequest) -> ExportResponse:
        data = request.data or {}
        filters = request.filters or {}
        filename = f"export_{request.report_type}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.{request.format}"
        content = ""
        size = 0
        if request.format == "csv":
            rows = data.get("rows", [])
            headers = data.get("headers", list(rows[0].keys()) if rows else [])
            content = self._generate_csv(rows, headers)
            size = len(content.encode("utf-8"))
        elif request.format == "json":
            content = self._generate_json(data)
            size = len(content.encode("utf-8"))
        elif request.format == "print":
            content = self._generate_json(data)
            size = len(content.encode("utf-8"))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported format: {request.format}")
        return ExportResponse(
            content=content,
            filename=filename,
            format=request.format,
            size_bytes=size,
        )

    async def generate_ai_report(self, officer: Dict[str, Any], request: AIReportRequest) -> AIReportResponse:
        scope = request.scope or {}
        analytics = request.analytics or {}
        try:
            from app.services.ai_service import ExecutiveIntelligenceService
            service = ExecutiveIntelligenceService(self.request)
            result = await service.generate_executive_summary(
                filters=scope.get("filters"),
                intelligence_scope=scope.get("intelligence_scope"),
                dashboard_payload=analytics,
            )
            sections = ["Executive Summary", "Key Findings", "Risk Assessment"]
            if request.report_type in ("operational", "predictive"):
                sections.extend(["Recommendations", "Appendix"])
            content = result.get("briefing", result.get("summary", "No content generated."))
            return AIReportResponse(
                report_id=f"AI-{request.report_type}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                title=f"{request.report_type.replace('_', ' ').title()} Report",
                content=content,
                format=request.format,
                generated_at=datetime.now(timezone.utc).isoformat(),
                confidence=result.get("confidence", 0.0),
                is_fallback=result.get("is_fallback", True),
                sections=sections,
            )
        except Exception as e:
            logger.error(f"AI report generation failed: {e}")
            return AIReportResponse(
                report_id=f"AI-{request.report_type}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                title=f"{request.report_type.replace('_', ' ').title()} Report",
                content="Report generation failed. Please try again.",
                format=request.format,
                generated_at=datetime.now(timezone.utc).isoformat(),
                confidence=0.0,
                is_fallback=True,
                sections=["Error"],
            )
