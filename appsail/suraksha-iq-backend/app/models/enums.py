from enum import Enum

class Role(str, Enum):
    STATE_COMMAND = "STATE_COMMAND"
    RANGE_IG = "RANGE_IG"
    DISTRICT_SP = "DISTRICT_SP"
    STATION_HOUSE_OFFICER = "STATION_HOUSE_OFFICER"
    INVESTIGATING_OFFICER = "INVESTIGATING_OFFICER"
    CID_ANALYST = "CID_ANALYST"
    SYSTEM_ADMINISTRATOR = "SYSTEM_ADMINISTRATOR"

class Permission(str, Enum):
    # Data Access
    VIEW_CRIMES = "VIEW_CRIMES"
    EDIT_CRIMES = "EDIT_CRIMES"
    VIEW_PII = "VIEW_PII"        # Highly restricted (Victim/Complainant PII)
    VIEW_ANALYTICS = "VIEW_ANALYTICS"
    
    # Administration
    MANAGE_USERS = "MANAGE_USERS"
    MANAGE_ROLES = "MANAGE_ROLES"
    MANAGE_ALERT_RULES = "MANAGE_ALERT_RULES"
    
    # Exports
    EXPORT_DATA = "EXPORT_DATA"

# Centralized Role to Permissions Mapping
ROLE_PERMISSIONS_MAP = {
    Role.SYSTEM_ADMINISTRATOR: [
        Permission.MANAGE_USERS,
        Permission.MANAGE_ROLES,
        Permission.MANAGE_ALERT_RULES,
        Permission.VIEW_CRIMES,
        Permission.VIEW_ANALYTICS,
    ],
    Role.STATE_COMMAND: [
        Permission.VIEW_CRIMES,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_DATA,
        Permission.VIEW_PII,
    ],
    Role.RANGE_IG: [
        Permission.VIEW_CRIMES,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_DATA,
    ],
    Role.DISTRICT_SP: [
        Permission.VIEW_CRIMES,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_DATA,
    ],
    Role.STATION_HOUSE_OFFICER: [
        Permission.VIEW_CRIMES,
        Permission.EDIT_CRIMES,
        Permission.VIEW_PII,
        Permission.EXPORT_DATA,
    ],
    Role.INVESTIGATING_OFFICER: [
        Permission.VIEW_CRIMES,
        Permission.EDIT_CRIMES,
        Permission.VIEW_PII,
    ],
    Role.CID_ANALYST: [
        Permission.VIEW_CRIMES,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_DATA,
    ],
}
