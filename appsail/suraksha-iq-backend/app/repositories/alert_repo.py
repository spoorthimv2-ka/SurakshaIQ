from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.alert import Alert
from app.models.officer import Officer
from app.models.enums import Role
from app.models.police_station import PoliceStation

class AlertRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _apply_jurisdiction_scope(self, query, officer: Officer):
        if officer.role in [Role.STATE_COMMAND, Role.SYSTEM_ADMINISTRATOR, Role.CID_ANALYST]:
            return query
        elif officer.role == Role.RANGE_IG:
            return query
        elif officer.role in [Role.DISTRICT_SP, Role.STATION_HOUSE_OFFICER, Role.INVESTIGATING_OFFICER]:
            if officer.police_station_id:
                subq = select(PoliceStation.district_id).where(PoliceStation.id == officer.police_station_id).scalar_subquery()
                # If district_id is null, it's a state-wide alert, which maybe lower roles shouldn't see?
                # For now, allow them to see district alerts OR state-wide alerts (district_id == None).
                query = query.where(
                    (Alert.district_id == subq) | (Alert.district_id.is_(None))
                )
            return query
        return query
