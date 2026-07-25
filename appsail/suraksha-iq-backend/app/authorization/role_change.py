from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from app.models.enums import Role
from app.authorization.permissions import PermissionRegistry


class RoleChangeRequest:
    def __init__(
        self,
        request_id: str,
        officer_id: str,
        current_role: str,
        requested_role: str,
        reason: str,
        requested_by: str,
        status: str = "PENDING",
        approved_by: Optional[str] = None,
        rejected_by: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self.request_id = request_id
        self.officer_id = officer_id
        self.current_role = current_role
        self.requested_role = requested_role
        self.reason = reason
        self.requested_by = requested_by
        self.status = status
        self.approved_by = approved_by
        self.rejected_by = rejected_by
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.updated_at = updated_at or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "officer_id": self.officer_id,
            "current_role": self.current_role,
            "requested_role": self.requested_role,
            "reason": self.reason,
            "requested_by": self.requested_by,
            "status": self.status,
            "approved_by": self.approved_by,
            "rejected_by": self.rejected_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class RoleChangeRequestService:
    @staticmethod
    def create_request(
        officer_id: str,
        current_role: str,
        requested_role: str,
        reason: str,
        requested_by: str,
    ) -> RoleChangeRequest:
        return RoleChangeRequest(
            request_id=f"RCR-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{officer_id}",
            officer_id=officer_id,
            current_role=current_role,
            requested_role=requested_role,
            reason=reason,
            requested_by=requested_by,
        )

    @staticmethod
    def validate_transition(current_role: str, requested_role: str) -> bool:
        try:
            Role(requested_role)
            return True
        except ValueError:
            return False
