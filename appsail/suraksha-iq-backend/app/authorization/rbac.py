from typing import Dict, Any, Optional, Set
from app.models.enums import Role, Permission, PermissionRegistry, RoleHierarchy
from app.authorization.role_change import RoleChangeRequestService


class RolePermissionResolver:
    @staticmethod
    def tier_requires(tier: str) -> Set[Permission]:
        return PermissionRegistry.get_permissions(Role.STATION_HOUSE_OFFICER)

    @staticmethod
    def resolve(role: Role) -> Dict[str, Any]:
        perms = PermissionRegistry.get_permissions(role)
        return {
            "role": role.value,
            "tier": PermissionRegistry.tier_for_role(role),
            "permissions": sorted([p.value for p in perms]),
            "jurisdiction": PermissionRegistry.jurisdiction_for_role(role).value,
        }

    @staticmethod
    def can(officer_role: Role, permission: Permission) -> bool:
        return PermissionRegistry.has_permission(officer_role, permission)

    @staticmethod
    def can_access_module(officer_role: Role, module: str) -> bool:
        mapping = {
            "dashboard": Permission.ACCESS_DASHBOARD,
            "hotspots": Permission.ACCESS_HOTSPOTS,
            "trends": Permission.ACCESS_TRENDS,
            "anomalies": Permission.ACCESS_ANOMALIES,
            "repeat-offenders": Permission.ACCESS_REPEAT_OFFENDERS,
            "network-analysis": Permission.ACCESS_NETWORK_ANALYSIS,
            "risk-scoring": Permission.ACCESS_RISK_SCORING,
            "predictive-intelligence": Permission.ACCESS_PREDICTIVE_INTELLIGENCE,
            "alerts": Permission.ACCESS_ALERTS,
            "reports": Permission.ACCESS_REPORTS,
            "admin": Permission.ACCESS_ADMIN,
            "crime-management": Permission.ACCESS_CRIME_MANAGEMENT,
            "fir-management": Permission.ACCESS_FIR_MANAGEMENT,
            "search": Permission.ACCESS_SEARCH,
            "ai-investigation": Permission.ACCESS_AI_INVESTIGATION,
            "evidence-analyzer": Permission.ACCESS_EVIDENCE_ANALYZER,
            "timeline": Permission.ACCESS_TIMELINE,
            "ai-reports": Permission.ACCESS_AI_REPORTS,
            "settings": Permission.ACCESS_SETTINGS,
            "notifications": Permission.ACCESS_NOTIFICATIONS,
            "district-comparison": Permission.ACCESS_DISTRICT_ANALYTICS,
            "alert-threshold-config": Permission.ACCESS_ALERT_THRESHOLD_CONFIG,
            "state-analytics": Permission.ACCESS_STATE_ANALYTICS,
            "master-data": Permission.ACCESS_MASTER_DATA,
            "user-management": Permission.ACCESS_USER_MANAGEMENT,
            "role-assignment": Permission.ACCESS_ROLE_ASSIGNMENT,
            "jurisdiction-assignment": Permission.ACCESS_JURISDICTION_ASSIGNMENT,
            "system-configuration": Permission.ACCESS_SYSTEM_CONFIGURATION,
        }
        perm = mapping.get(module)
        if not perm:
            return False
        return PermissionRegistry.has_permission(officer_role, perm)
