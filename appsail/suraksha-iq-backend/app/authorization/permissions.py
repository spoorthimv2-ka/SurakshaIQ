from enum import Enum
from typing import Set, Dict, Any, Optional
from fastapi import HTTPException, status

from app.models.enums import Role, Permission, JurisdictionType, ROLE_TIER_MAP, ROLE_JURISDICTION_MAP, TIER_PERMISSIONS

class PermissionRegistry:
    @staticmethod
    def tier_for_role(role: Role) -> str:
        return ROLE_TIER_MAP.get(role, "OFFICER")

    @classmethod
    def get_permissions(cls, role: Role) -> Set[Permission]:
        tier = cls.tier_for_role(role)
        return TIER_PERMISSIONS.get(tier, set())

    @classmethod
    def has_permission(cls, role: Role, permission: Permission) -> bool:
        return permission in cls.get_permissions(role)

    @classmethod
    def has_any(cls, role: Role, permissions: list[Permission]) -> bool:
        role_perms = cls.get_permissions(role)
        return any(p in role_perms for p in permissions)

    @classmethod
    def has_all(cls, role: Role, permissions: list[Permission]) -> bool:
        role_perms = cls.get_permissions(role)
        return all(p in role_perms for p in permissions)

    @staticmethod
    def jurisdiction_for_role(role: Role) -> JurisdictionType:
        return ROLE_JURISDICTION_MAP.get(role, JurisdictionType.STATION)

class RoleHierarchy:
    @staticmethod
    def is_authorized(actor_tier: str, required_tier: str) -> bool:
        tier_order = ["OFFICER", "INSPECTOR", "DSP", "SP", "ADMIN"]
        try:
            return tier_order.index(actor_tier) >= tier_order.index(required_tier)
        except ValueError:
            return False

class PermissionResolver:
    @staticmethod
    def resolve_module_permissions(module: str) -> Set[Permission]:
        mapping: Dict[str, Permission] = {
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
        if perm:
            return {perm}
        return set()
