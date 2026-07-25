# Authorization Package Usage

## Overview

This package provides a centralized, policy-driven RBAC system for SurakshaIQ.

## Components

### PermissionRegistry (`permissions.py`)
Resolves permissions for roles using tier-based inheritance.

```python
from app.models.enums import Role, Permission
from app.authorization.permissions import PermissionRegistry

# Get all permissions for a role
perms = PermissionRegistry.get_permissions(Role.STATION_HOUSE_OFFICER)

# Check a specific permission
has = PermissionRegistry.has_permission(Role.CID_ANALYST, Permission.ACCESS_NETWORK_ANALYSIS)

# Check any/all permissions
has_any = PermissionRegistry.has_any(role, [Permission.ACCESS_DASHBOARD, Permission.ACCESS_REPORTS])
has_all = PermissionRegistry.has_all(role, [Permission.ACCESS_DASHBOARD, Permission.ACCESS_REPORTS])

# Get required jurisdiction for a role
jurisdiction = PermissionRegistry.jurisdiction_for_role(Role.DISTRICT_SP)
```

### RoleHierarchy (`permissions.py`)
Checks if an actor's tier meets a required tier.

```python
from app.authorization.permissions import RoleHierarchy

authorized = RoleHierarchy.is_authorized("DSP", "INSPECTOR")  # True
```

### PermissionResolver (`permissions.py`)
Resolves permissions for frontend modules.

```python
from app.authorization.permissions import PermissionResolver

perms = PermissionResolver.resolve_module_permissions("district-analytics")
```

### AuthorizationService (`service.py`)
Provides `get_current_officer`, `RequirePermission`, and `enforce_jurisdiction`.

```python
from app.api.deps import get_current_officer, RequirePermission, enforce_jurisdiction

# Use in route dependencies
@router.get("/crimes")
async def get_crimes(current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_CRIME_MANAGEMENT]))):
    pass

# Enforce jurisdiction in services
enforce_jurisdiction(officer, target_district_id=district_id, target_station_id=station_id)
```

### MFA (`mfa.py`)
Future MFA support. Implement `MFAProtocol` and use `AuthenticationFactory`.

```python
from app.authorization.mfa import AuthenticationFactory, MFAProtocol

class CustomMFA(MFAProtocol):
    async def initiate(self, user_id, channel):
        ...
    async def verify(self, user_id, code, channel):
        ...

factory = AuthenticationFactory()
mfa = factory.create_mfa()
```

### RoleChangeRequest (`role_change.py`)
Prepare role changes for approval workflows.

```python
from app.authorization.role_change import RoleChangeRequestService

request = RoleChangeRequestService.create_request(
    officer_id=officer_id,
    current_role="STATION_HOUSE_OFFICER",
    requested_role="INVESTIGATING_OFFICER",
    reason="Promotion",
    requested_by=admin_id,
)
```

## Adding New Permissions

1. Add the permission to `Permission` enum in `app/models/enums.py`.
2. Assign it to the appropriate tier in `TIER_PERMISSIONS` in `app/models/enums.py`.
3. Map it to a frontend module in `PermissionResolver.resolve_module_permissions` in `app/authorization/permissions.py`.
4. Map it to a frontend route in `client/src/utils/permissions.ts`.

## Adding New Roles

1. Add the role to `Role` enum in `app/models/enums.py`.
2. Assign it a tier in `ROLE_TIER_MAP`.
3. Assign it a jurisdiction in `ROLE_JURISDICTION_MAP`.
4. The role automatically inherits all permissions from lower tiers via `TIER_PERMISSIONS`.
