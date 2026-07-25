from enum import Enum
from typing import Set


class JurisdictionType(str, Enum):
    STATION = "STATION"
    DISTRICT = "DISTRICT"
    STATE = "STATE"


class AccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    INACTIVE = "INACTIVE"


class Role(str, Enum):
    STATION_HOUSE_OFFICER = "STATION_HOUSE_OFFICER"
    INVESTIGATING_OFFICER = "INVESTIGATING_OFFICER"
    CID_ANALYST = "CID_ANALYST"
    DISTRICT_SP = "DISTRICT_SP"
    STATE_COMMAND = "STATE_COMMAND"
    RANGE_IG = "RANGE_IG"
    SYSTEM_ADMINISTRATOR = "SYSTEM_ADMINISTRATOR"


class Permission(str, Enum):
    # Module Access
    ACCESS_DASHBOARD = "access_dashboard"
    ACCESS_HOTSPOTS = "access_hotspots"
    ACCESS_TRENDS = "access_trends"
    ACCESS_ANOMALIES = "access_anomalies"
    ACCESS_REPEAT_OFFENDERS = "access_repeat_offenders"
    ACCESS_NETWORK_ANALYSIS = "access_network_analysis"
    ACCESS_RISK_SCORING = "access_risk_scoring"
    ACCESS_PREDICTIVE_INTELLIGENCE = "access_predictive_intelligence"
    ACCESS_ALERTS = "access_alerts"
    ACCESS_REPORTS = "access_reports"
    ACCESS_ADMIN = "access_admin"
    ACCESS_CRIME_MANAGEMENT = "access_crime_management"
    ACCESS_FIR_MANAGEMENT = "access_fir_management"
    ACCESS_SEARCH = "access_search"
    ACCESS_AI_INVESTIGATION = "access_ai_investigation"
    ACCESS_EVIDENCE_ANALYZER = "access_evidence_analyzer"
    ACCESS_TIMELINE = "access_timeline"
    ACCESS_AI_REPORTS = "access_ai_reports"
    ACCESS_SETTINGS = "access_settings"
    ACCESS_NOTIFICATIONS = "access_notifications"
    ACCESS_DISTRICT_ANALYTICS = "access_district_analytics"
    ACCESS_ALERT_THRESHOLD_CONFIG = "access_alert_threshold_config"
    ACCESS_STATE_ANALYTICS = "access_state_analytics"
    ACCESS_MASTER_DATA = "access_master_data"
    ACCESS_USER_MANAGEMENT = "access_user_management"
    ACCESS_ROLE_ASSIGNMENT = "access_role_assignment"
    ACCESS_JURISDICTION_ASSIGNMENT = "access_jurisdiction_assignment"
    ACCESS_SYSTEM_CONFIGURATION = "access_system_configuration"

    # Actions
    VIEW_PII = "view_pii"
    EXPORT_DATA = "export_data"
    EDIT_CRIMES = "edit_crimes"


ROLE_TIER_MAP = {
    Role.STATION_HOUSE_OFFICER: "OFFICER",
    Role.INVESTIGATING_OFFICER: "OFFICER",
    Role.CID_ANALYST: "INSPECTOR",
    Role.DISTRICT_SP: "DSP",
    Role.STATE_COMMAND: "SP",
    Role.RANGE_IG: "SP",
    Role.SYSTEM_ADMINISTRATOR: "ADMIN",
}

ROLE_JURISDICTION_MAP = {
    Role.STATION_HOUSE_OFFICER: JurisdictionType.STATION,
    Role.INVESTIGATING_OFFICER: JurisdictionType.STATION,
    Role.CID_ANALYST: JurisdictionType.DISTRICT,
    Role.DISTRICT_SP: JurisdictionType.DISTRICT,
    Role.STATE_COMMAND: JurisdictionType.STATE,
    Role.RANGE_IG: JurisdictionType.STATE,
    Role.SYSTEM_ADMINISTRATOR: JurisdictionType.STATE,
}

ADMIN_PERMS = {
    Permission.ACCESS_ADMIN,
    Permission.ACCESS_MASTER_DATA,
    Permission.ACCESS_USER_MANAGEMENT,
    Permission.ACCESS_ROLE_ASSIGNMENT,
    Permission.ACCESS_JURISDICTION_ASSIGNMENT,
    Permission.ACCESS_SYSTEM_CONFIGURATION,
    Permission.VIEW_PII,
}

TIER_PERMISSIONS: dict[str, Set[Permission]] = {
    "OFFICER": {
        Permission.ACCESS_DASHBOARD,
        Permission.ACCESS_FIR_MANAGEMENT,
        Permission.ACCESS_ALERTS,
        Permission.ACCESS_CRIME_MANAGEMENT,
        Permission.ACCESS_REPEAT_OFFENDERS,
        Permission.ACCESS_SEARCH,
        Permission.ACCESS_AI_INVESTIGATION,
        Permission.ACCESS_EVIDENCE_ANALYZER,
        Permission.ACCESS_TIMELINE,
        Permission.ACCESS_AI_REPORTS,
        Permission.ACCESS_SETTINGS,
        Permission.ACCESS_NOTIFICATIONS,
        Permission.ACCESS_HOTSPOTS,
        Permission.EDIT_CRIMES,
        Permission.EXPORT_DATA,
    },
    "INSPECTOR": {
        Permission.ACCESS_TRENDS,
        Permission.ACCESS_ANOMALIES,
        Permission.ACCESS_NETWORK_ANALYSIS,
        Permission.ACCESS_RISK_SCORING,
        Permission.ACCESS_PREDICTIVE_INTELLIGENCE,
        Permission.ACCESS_REPORTS,
        Permission.ACCESS_DISTRICT_ANALYTICS,
    },
    "DSP": {
        Permission.ACCESS_ALERT_THRESHOLD_CONFIG,
    },
    "SP": {
        Permission.ACCESS_STATE_ANALYTICS,
    },
    "ADMIN": set(),
}

TIER_PERMISSIONS["INSPECTOR"] = TIER_PERMISSIONS["INSPECTOR"] | TIER_PERMISSIONS["OFFICER"]
TIER_PERMISSIONS["DSP"] = TIER_PERMISSIONS["DSP"] | TIER_PERMISSIONS["INSPECTOR"]
TIER_PERMISSIONS["SP"] = TIER_PERMISSIONS["SP"] | TIER_PERMISSIONS["DSP"]
TIER_PERMISSIONS["ADMIN"] = ADMIN_PERMS | TIER_PERMISSIONS["SP"]
