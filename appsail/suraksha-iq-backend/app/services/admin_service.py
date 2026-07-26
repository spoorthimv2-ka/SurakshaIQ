from typing import Any, Dict, List, Optional
from fastapi import Request
from app.repositories.admin_repo import AdminRepository
from app.repositories.user_repo import UserRepository
from app.repositories.officer_repo import OfficerRepository
from app.repositories.district_repo import DistrictRepository
from app.repositories.police_station_repo import PoliceStationRepository
from app.core.logger import logger
from app.core.exceptions import DataValidationError, RepositoryError
from zcatalyst_sdk.exceptions import CatalystError
from collections import defaultdict

class AdminService:
    """Service layer for Admin operations."""

    def __init__(self, request: Request, repo: AdminRepository):
        self.request = request
        self.repo = repo
        self.user_repo = UserRepository(request)
        self.officer_repo = OfficerRepository(request)
        self.district_repo = DistrictRepository(request)
        self.station_repo = PoliceStationRepository(request)

    async def get_users(self, limit: int = 100, offset: int = 0, role: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves users with optional filters, merged with officer data."""
        logger.info("Fetching users for admin")
        users = await self.repo.find_users(limit=limit, offset=offset, role=role, status=status)
        officers = await self.officer_repo.find_all(limit=1000)
        officer_map: Dict[str, Dict[str, Any]] = {}
        for o in officers:
            for key in ("user_id", "catalyst_user_id"):
                val = o.get(key)
                if val:
                    officer_map[str(val)] = o

        stations = await self.station_repo.find_all(limit=1000)
        station_map = {s.get("ROWID", ""): s for s in stations}

        districts = await self.district_repo.find_all(limit=1000)
        district_map = {d.get("ROWID", ""): d for d in districts}

        result = []
        for u in users:
            officer = officer_map.get(u.get("ROWID", ""), {})
            station_id = officer.get("station_id", "")
            station = station_map.get(station_id, {})
            district_id = station.get("district_id", "")
            district = district_map.get(district_id, {})

            result.append({
                "user_id": u.get("ROWID", ""),
                "officer_id": officer.get("ROWID"),
                "name": officer.get("name", ""),
                "email": u.get("email", officer.get("email", "")),
                "role": u.get("role", ""),
                "district": district.get("name", district_id) if district_id else None,
                "station": station.get("name", station_id) if station_id else None,
                "status": u.get("status", "ACTIVE"),
                "created_at": u.get("CREATEDTIME", ""),
                "updated_at": u.get("MODIFIEDTIME", ""),
            })
        return result[offset:offset+limit]

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single user by ID, merged with officer data."""
        logger.info(f"Fetching user {user_id}")
        user = await self.repo.find_user(user_id)
        if not user:
            return None

        officer = await self.repo.find_officer_by_user_id(user_id)
        station_id = officer.get("station_id", "") if officer else ""
        station = await self.station_repo.find_by_id(station_id) if station_id else {}
        district_id = station.get("district_id", "") if station else ""
        district = await self.district_repo.find_by_id(district_id) if district_id else {}

        return {
            "user_id": user.get("ROWID", ""),
            "officer_id": officer.get("ROWID") if officer else None,
            "name": officer.get("name", "") if officer else "",
            "email": user.get("email", officer.get("email", "") if officer else ""),
            "role": user.get("role", ""),
            "district": district.get("name", district_id) if district_id else None,
            "station": station.get("name", station_id) if station_id else None,
            "status": user.get("status", "ACTIVE"),
            "created_at": user.get("CREATEDTIME", ""),
            "updated_at": user.get("MODIFIEDTIME", ""),
        }

    async def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new user."""
        logger.info("Creating user")
        if not data.get("email"):
            raise DataValidationError("Email is required")
        if not data.get("role"):
            raise DataValidationError("Role is required")

        existing = await self.user_repo.find_by_email(data["email"])
        if existing:
            raise DataValidationError(f"User with email {data['email']} already exists")

        user_data = {
            "email": data["email"],
            "role": data["role"],
            "status": data.get("status", "ACTIVE"),
        }
        user = await self.repo.create_user(user_data)

        if data.get("name"):
            officer_data = {
                "user_id": user.get("ROWID", ""),
                "name": data["name"],
                "email": data["email"],
                "role": data["role"],
                "badge_number": f"AUTO-{user.get('ROWID', '')[:8]}",
                "status": data.get("status", "ACTIVE"),
                "station_id": data.get("station"),
            }
            await self.officer_repo.create(officer_data)

        return await self.get_user(user.get("ROWID", ""))

    async def update_user(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing user."""
        logger.info(f"Updating user {user_id}")
        existing = await self.repo.find_user(user_id)
        if not existing:
            raise DataValidationError(f"User {user_id} not found")

        update_data = {}
        if data.get("email"):
            update_data["email"] = data["email"]
        if data.get("role"):
            update_data["role"] = data["role"]
        if data.get("status"):
            update_data["status"] = data["status"]

        if update_data:
            await self.repo.update_user(user_id, update_data)

        officer = await self.repo.find_officer_by_user_id(user_id)
        if officer and (data.get("name") or data.get("station")):
            officer_update = {}
            if data.get("name"):
                officer_update["name"] = data["name"]
            if data.get("station"):
                officer_update["station_id"] = data["station"]
            if officer_update:
                await self.officer_repo.update(officer.get("ROWID", ""), officer_update)

        return await self.get_user(user_id)

    async def delete_user(self, user_id: str) -> bool:
        """Deletes a user."""
        logger.info(f"Deleting user {user_id}")
        existing = await self.repo.find_user(user_id)
        if not existing:
            raise DataValidationError(f"User {user_id} not found")
        result = await self.repo.delete_user(user_id)
        logger.info("User deleted")
        return result

    async def activate_user(self, user_id: str) -> Dict[str, Any]:
        """Activates a user."""
        logger.info(f"Activating user {user_id}")
        existing = await self.repo.find_user(user_id)
        if not existing:
            raise DataValidationError(f"User {user_id} not found")
        await self.repo.activate_user(user_id)
        logger.info("User activated")
        return await self.get_user(user_id)

    async def deactivate_user(self, user_id: str) -> Dict[str, Any]:
        """Deactivates a user."""
        logger.info(f"Deactivating user {user_id}")
        existing = await self.repo.find_user(user_id)
        if not existing:
            raise DataValidationError(f"User {user_id} not found")
        await self.repo.deactivate_user(user_id)
        logger.info("User deactivated")
        return await self.get_user(user_id)

    async def get_roles(self) -> List[Dict[str, str]]:
        """Returns available roles."""
        logger.info("Fetching roles")
        return await self.repo.get_roles()

    async def get_statistics(self) -> Dict[str, Any]:
        """Returns admin statistics."""
        logger.info("Fetching statistics")
        return await self.repo.get_statistics()

    async def get_audit_logs(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieves audit logs."""
        logger.info("Fetching audit logs")
        return await self.repo.get_audit_logs(limit=limit, offset=offset)

    async def create_audit_log(self, action: str, user_id: str, target: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Creates an audit log entry."""
        logger.info(f"Creating audit log: {action} by {user_id} on {target}")
        import uuid
        from datetime import datetime, timezone
        from app.core.utils import catalyst_datetime
        log_data = {
            "log_id": str(uuid.uuid4()),
            "action": action,
            "user_id": user_id,
            "target": target,
            "event_timestamp": catalyst_datetime(),
            "metadata": metadata or {},
        }
        return await self.repo.create_audit_log(log_data)

    async def list_officers(self, limit: int = 100, offset: int = 0, station_id: Optional[str] = None, district_id: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            officers = await self.officer_repo.find_all(limit=1000)
            stations = await self.station_repo.find_all(limit=1000)
            district_map = {d.get("ROWID", ""): d for d in await self.district_repo.find_all(limit=1000)}
            result = []
            for o in officers:
                sid = o.get("station_id", "")
                station = next((s for s in stations if s.get("ROWID") == sid), {})
                did = station.get("district_id", "")
                district = district_map.get(did, {})
                if station_id and sid != station_id:
                    continue
                if district_id and did != district_id:
                    continue
                result.append({
                    "officer_id": o.get("ROWID", ""),
                    "name": o.get("name", ""),
                    "email": o.get("email", ""),
                    "role": o.get("role", ""),
                    "rank": o.get("rank", ""),
                    "designation": o.get("designation", ""),
                    "station_id": sid,
                    "station_name": station.get("name", sid),
                    "district_id": did,
                    "district_name": district.get("name", did),
                    "status": o.get("status", "ACTIVE"),
                    "badge_number": o.get("badge_number", ""),
                })
            return result[offset:offset+limit]
        except CatalystError as e:
            logger.error(f"Error fetching officers: {e}")
            raise RepositoryError(f"Failed to fetch officers: {e}")

    async def list_districts(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        try:
            districts = await self.district_repo.find_all(limit=1000)
            stations = await self.station_repo.find_all(limit=1000)
            officers = await self.officer_repo.find_all(limit=1000)
            station_count: Dict[str, int] = defaultdict(int)
            for s in stations:
                did = s.get("district_id", "")
                if did:
                    station_count[did] += 1
            officer_count: Dict[str, int] = defaultdict(int)
            for o in officers:
                sid = o.get("station_id", "")
                if sid:
                    station = next((s for s in stations if s.get("ROWID") == sid), None)
                    if station:
                        did = station.get("district_id", "")
                        if did:
                            officer_count[did] += 1
            result = []
            for d in districts:
                did = d.get("ROWID", "")
                result.append({
                    "district_id": did,
                    "district_name": d.get("name", ""),
                    "state": d.get("state", ""),
                    "region_code": d.get("region_code", ""),
                    "status": d.get("status", "ACTIVE"),
                    "station_count": station_count.get(did, 0),
                    "officer_count": officer_count.get(did, 0),
                })
            return result[offset:offset+limit]
        except CatalystError as e:
            logger.error(f"Error fetching districts: {e}")
            raise RepositoryError(f"Failed to fetch districts: {e}")

    async def list_police_stations(self, limit: int = 100, offset: int = 0, district_id: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            stations = await self.station_repo.find_all(limit=1000)
            districts = await self.district_repo.find_all(limit=1000)
            district_map = {d.get("ROWID", ""): d for d in districts}
            officers = await self.officer_repo.find_all(limit=1000)
            officer_count: Dict[str, int] = defaultdict(int)
            for o in officers:
                sid = o.get("station_id", "")
                if sid:
                    officer_count[sid] += 1
            result = []
            for s in stations:
                did = s.get("district_id", "")
                if district_id and did != district_id:
                    continue
                district = district_map.get(did, {})
                result.append({
                    "station_id": s.get("ROWID", ""),
                    "station_name": s.get("name", ""),
                    "district_id": did,
                    "district_name": district.get("name", did),
                    "station_code": s.get("station_code", ""),
                    "address": s.get("address", ""),
                    "status": s.get("status", "ACTIVE"),
                    "officer_count": officer_count.get(s.get("ROWID", ""), 0),
                    "latitude": s.get("latitude"),
                    "longitude": s.get("longitude"),
                })
            return result[offset:offset+limit]
        except CatalystError as e:
            logger.error(f"Error fetching police stations: {e}")
            raise RepositoryError(f"Failed to fetch police stations: {e}")
