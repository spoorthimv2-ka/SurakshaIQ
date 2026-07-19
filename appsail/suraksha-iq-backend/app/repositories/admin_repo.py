from typing import List, Dict, Any, Optional
from app.repositories.base_repository import BaseCatalystRepository
from app.repositories.user_repo import UserRepository
from app.repositories.officer_repo import OfficerRepository
from app.repositories.district_repo import DistrictRepository
from app.repositories.police_station_repo import PoliceStationRepository
from app.core.exceptions import RepositoryError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger

class AdminRepository(BaseCatalystRepository):
    """
    Repository for admin operations backed by Catalyst Data Store.
    Reuses existing repositories for data retrieval.
    """

    def __init__(self):
        super().__init__(table_name="User")
        self.user_repo = UserRepository()
        self.officer_repo = OfficerRepository()
        self.district_repo = DistrictRepository()
        self.station_repo = PoliceStationRepository()

    async def find_users(self, limit: int = 100, offset: int = 0, role: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves users with optional filters, merged with officer data."""
        try:
            offset_val = offset if offset > 0 else 1
            query = f"SELECT * FROM {self.table_name} WHERE 1=1"
            if role:
                query += f" AND role = '{role}'"
            if status:
                query += f" AND status = '{status}'"
            query += f" ORDER BY CREATEDTIME DESC LIMIT {offset_val}, {limit}"
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if self.table_name in item:
                    rows.append(item[self.table_name])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching users: {e}")
            raise RepositoryError(f"Failed to fetch users: {e}")

    async def find_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single user by ROWID."""
        try:
            return await self.user_repo.find_by_id(user_id)
        except CatalystError as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            raise RepositoryError(f"Failed to fetch user: {e}")

    async def find_officer_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves officer profile by user ID."""
        try:
            return await self.officer_repo.find_by_user_id(user_id)
        except CatalystError as e:
            logger.error(f"Error fetching officer for user {user_id}: {e}")
            raise RepositoryError(f"Failed to fetch officer: {e}")

    async def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new user in the User table."""
        try:
            return await self.user_repo.create(data)
        except CatalystError as e:
            logger.error(f"Error creating user: {e}")
            raise RepositoryError(f"Failed to create user: {e}")

    async def update_user(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing user."""
        try:
            return await self.user_repo.update(user_id, data)
        except CatalystError as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise RepositoryError(f"Failed to update user: {e}")

    async def delete_user(self, user_id: str) -> bool:
        """Deletes a user."""
        try:
            return await self.user_repo.delete(user_id)
        except CatalystError as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise RepositoryError(f"Failed to delete user: {e}")

    async def activate_user(self, user_id: str) -> Dict[str, Any]:
        """Activates a user."""
        try:
            return await self.user_repo.update(user_id, {"status": "ACTIVE"})
        except CatalystError as e:
            logger.error(f"Error activating user {user_id}: {e}")
            raise RepositoryError(f"Failed to activate user: {e}")

    async def deactivate_user(self, user_id: str) -> Dict[str, Any]:
        """Deactivates a user."""
        try:
            return await self.user_repo.update(user_id, {"status": "INACTIVE"})
        except CatalystError as e:
            logger.error(f"Error deactivating user {user_id}: {e}")
            raise RepositoryError(f"Failed to deactivate user: {e}")

    async def get_roles(self) -> List[Dict[str, str]]:
        """Returns available roles."""
        from app.models.enums import Role
        roles = [
            (Role.SYSTEM_ADMINISTRATOR, "Super Admin", "Full system access with all permissions"),
            (Role.STATE_COMMAND, "Admin", "State-level administrative access"),
            (Role.RANGE_IG, "District Officer", "Range-level oversight and management"),
            (Role.DISTRICT_SP, "District Officer", "District-level command and review"),
            (Role.STATION_HOUSE_OFFICER, "Station Officer", "Station-level operations management"),
            (Role.INVESTIGATING_OFFICER, "Analyst", "Investigation and case analysis"),
            (Role.CID_ANALYST, "Analyst", "Criminal intelligence analysis"),
        ]
        return [{"id": r.value, "label": label, "description": desc} for r, label, desc in roles]

    async def get_statistics(self) -> Dict[str, Any]:
        """Returns admin statistics."""
        try:
            total = await self.user_repo.count()
            active = await self.user_repo.find_active(limit=1000)
            inactive_query = f"SELECT COUNT(ROWID) FROM {self.table_name} WHERE status = 'INACTIVE'"
            inactive_result = self.zcql.execute_query(inactive_query)
            inactive = 0
            if inactive_result and len(inactive_result) > 0:
                first_row = inactive_result[0]
                for table_data in first_row.values():
                    for val in table_data.values():
                        if isinstance(val, (int, float, str)) and str(val).isdigit():
                            inactive = int(val)
                            break

            users = await self.user_repo.find_all(limit=1000)
            officers = await self.officer_repo.find_all(limit=1000)
            officer_map = {o.get("user_id", ""): o for o in officers}

            by_role: Dict[str, int] = {}
            by_district: Dict[str, int] = {}
            for u in users:
                role = u.get("role", "UNKNOWN")
                by_role[role] = by_role.get(role, 0) + 1
                officer = officer_map.get(u.get("ROWID", ""))
                if officer:
                    station_id = officer.get("station_id", "")
                    if station_id:
                        station = await self.station_repo.find_by_id(station_id)
                        district_id = station.get("district_id", "UNKNOWN") if station else "UNKNOWN"
                        by_district[district_id] = by_district.get(district_id, 0) + 1

            district_names = {}
            for did in by_district.keys():
                if did and did != "UNKNOWN":
                    d = await self.district_repo.find_by_id(did)
                    if d:
                        district_names[did] = d.get("name", did)

            return {
                "total_users": total,
                "active_users": len(active),
                "inactive_users": inactive,
                "users_by_role": [{"role": k, "count": v} for k, v in sorted(by_role.items())],
                "users_by_district": [
                    {"district_id": k, "district_name": district_names.get(k, k), "count": v}
                    for k, v in sorted(by_district.items(), key=lambda x: x[1], reverse=True)
                ],
            }
        except CatalystError as e:
            logger.error(f"Error fetching statistics: {e}")
            raise RepositoryError(f"Failed to fetch statistics: {e}")

    async def get_audit_logs(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieves audit logs."""
        try:
            offset_val = offset if offset > 0 else 1
            query = f"SELECT * FROM AuditLog ORDER BY CREATEDTIME DESC LIMIT {offset_val}, {limit}"
            result = self.zcql.execute_query(query)
            
            rows = []
            for item in result:
                if "AuditLog" in item:
                    rows.append(item["AuditLog"])
            return rows
        except CatalystError as e:
            logger.error(f"Error fetching audit logs: {e}")
            raise RepositoryError(f"Failed to fetch audit logs: {e}")

    async def create_audit_log(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates an audit log entry."""
        try:
            table = self.datastore.table("AuditLog")
            return table.insert_row(data)
        except CatalystError as e:
            logger.error(f"Error creating audit log: {e}")
            raise RepositoryError(f"Failed to create audit log: {e}")
