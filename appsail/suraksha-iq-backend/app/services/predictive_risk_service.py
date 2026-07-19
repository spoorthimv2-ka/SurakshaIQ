from typing import Any, Dict, List, Optional
from datetime import datetime, timezone, timedelta

from app.repositories.predictive_risk_repo import PredictiveRiskRepository
from app.repositories.crime_repo import CrimeRepository
from app.repositories.fir_repo import FIRRepository
from app.repositories.district_repo import DistrictRepository
from app.repositories.police_station_repo import PoliceStationRepository
from app.repositories.hotspot_repo import HotspotRepository
from app.repositories.repeat_offender_repo import RepeatOffenderRepository
from app.core.logger import logger
from app.schemas.risk import (
    RiskPrediction,
    RiskFactor,
    DistrictRisk,
    StationRisk,
    RiskSummary,
)


class PredictiveRiskService:
    """Service layer for predictive risk analysis."""

    def __init__(self):
        self.repo = PredictiveRiskRepository()
        self.crime_repo = CrimeRepository()
        self.fir_repo = FIRRepository()
        self.district_repo = DistrictRepository()
        self.station_repo = PoliceStationRepository()
        self.hotspot_repo = HotspotRepository()
        self.repeat_offender_repo = RepeatOffenderRepository()

    async def get_predictions(self, officer: Dict[str, Any], limit: int = 100) -> List[RiskPrediction]:
        """Retrieves risk predictions for all districts and stations."""
        del officer
        data = await self.repo.get_risk_data(limit=limit)
        predictions: List[RiskPrediction] = []

        for district in data.get("districts", []):
            did = district.get("ROWID", district.get("id", ""))
            dname = district.get("name", did)
            score, factors, level = self._compute_risk(data, entity_id=did, entity_type="District", entity_name=dname)
            predictions.append(
                RiskPrediction(
                    entity_id=did,
                    entity_type="District",
                    entity_name=dname,
                    risk_score=round(score, 2),
                    risk_level=level,
                    contributing_factors=factors,
                    last_updated=datetime.now(timezone.utc).isoformat(),
                )
            )

        for station in data.get("stations", []):
            sid = station.get("ROWID", station.get("id", ""))
            sname = station.get("name", sid)
            score, factors, level = self._compute_risk(data, entity_id=sid, entity_type="PoliceStation", entity_name=sname)
            predictions.append(
                RiskPrediction(
                    entity_id=sid,
                    entity_type="PoliceStation",
                    entity_name=sname,
                    risk_score=round(score, 2),
                    risk_level=level,
                    contributing_factors=factors,
                    last_updated=datetime.now(timezone.utc).isoformat(),
                )
            )

        predictions.sort(key=lambda x: x.risk_score, reverse=True)
        return predictions

    async def get_summary(self, officer: Dict[str, Any]) -> RiskSummary:
        """Retrieves aggregated risk summary."""
        del officer
        predictions = await self.get_predictions(officer, limit=1000)
        if not predictions:
            return RiskSummary(
                total_entities=0,
                average_risk=0.0,
                highest_risk_district="-",
                highest_risk_station="-",
                total_high_risk=0,
                total_critical_risk=0,
                risk_distribution=[],
            )

        total = len(predictions)
        average_risk = sum(p.risk_score for p in predictions) / total
        high_risk = [p for p in predictions if p.risk_level == "HIGH"]
        critical_risk = [p for p in predictions if p.risk_level == "CRITICAL"]

        district_predictions = [p for p in predictions if p.entity_type == "District"]
        station_predictions = [p for p in predictions if p.entity_type == "PoliceStation"]

        highest_risk_district = district_predictions[0].entity_name if district_predictions else "-"
        highest_risk_station = station_predictions[0].entity_name if station_predictions else "-"

        distribution: List[dict] = []
        for p in predictions:
            distribution.append(
                {
                    "entity_id": p.entity_id,
                    "entity_type": p.entity_type,
                    "entity_name": p.entity_name,
                    "risk_score": p.risk_score,
                    "risk_level": p.risk_level,
                }
            )

        return RiskSummary(
            total_entities=total,
            average_risk=round(average_risk, 2),
            highest_risk_district=highest_risk_district,
            highest_risk_station=highest_risk_station,
            total_high_risk=len(high_risk),
            total_critical_risk=len(critical_risk),
            risk_distribution=distribution,
        )

    async def get_district_predictions(self, officer: Dict[str, Any]) -> List[DistrictRisk]:
        """Retrieves risk predictions for all districts."""
        del officer
        predictions = await self.get_predictions(officer, limit=1000)
        district_risks: List[DistrictRisk] = []
        for p in predictions:
            if p.entity_type != "District":
                continue
            district_risks.append(
                DistrictRisk(
                    district_id=p.entity_id,
                    district_name=p.entity_name,
                    risk_score=p.risk_score,
                    risk_level=p.risk_level,
                    crime_count=0,
                    fir_count=0,
                    hotspot_score=0.0,
                    repeat_offender_count=0,
                    contributing_factors=p.contributing_factors,
                )
            )
        return district_risks

    async def get_station_predictions(self, officer: Dict[str, Any]) -> List[StationRisk]:
        """Retrieves risk predictions for all police stations."""
        del officer
        predictions = await self.get_predictions(officer, limit=1000)
        station_risks: List[StationRisk] = []
        for p in predictions:
            if p.entity_type != "PoliceStation":
                continue
            district_name = "-"
            for district in (await self.district_repo.find_active(limit=1000)):
                if district.get("ROWID") == p.entity_id or district.get("id") == p.entity_id:
                    district_name = district.get("name", "-")
                    break
            station_risks.append(
                StationRisk(
                    station_id=p.entity_id,
                    station_name=p.entity_name,
                    district_id="-",
                    district_name=district_name,
                    risk_score=p.risk_score,
                    risk_level=p.risk_level,
                    crime_count=0,
                    fir_count=0,
                    hotspot_score=0.0,
                    contributing_factors=p.contributing_factors,
                )
            )
        return station_risks

    async def get_entity_prediction(self, officer: Dict[str, Any], entity_id: str, entity_type: str = "District") -> Optional[RiskPrediction]:
        """Retrieves risk prediction for a specific entity."""
        del officer
        predictions = await self.get_predictions(officer, limit=1000)
        for p in predictions:
            if p.entity_id == entity_id and p.entity_type == entity_type:
                return p
        return None

    def _compute_risk(self, data: Dict[str, Any], entity_id: str, entity_type: str, entity_name: str) -> tuple[float, List[RiskFactor], str]:
        """Computes a deterministic risk score for an entity."""
        factors: List[RiskFactor] = []
        score = 0.0

        crimes = data.get("crimes", [])
        firs = data.get("firs", [])
        criminals = data.get("criminals", [])

        if entity_type == "District":
            entity_crimes = [c for c in crimes if c.get("district_id") == entity_id]
            entity_firs = [f for f in firs if f.get("district_id") == entity_id]
        else:
            entity_crimes = [c for c in crimes if c.get("station_id") == entity_id]
            entity_firs = [f for f in firs if f.get("station_id") == entity_id]

        crime_count = len(entity_crimes)
        fir_count = len(entity_firs)

        if crime_count > 0:
            weight = min(crime_count * 2.0, 30.0)
            score += weight
            factors.append(RiskFactor(name="Crime Frequency", weight=weight, contribution=crime_count))

        unresolved_firs = [f for f in entity_firs if f.get("status") == "ACTIVE"]
        unresolved_ratio = len(unresolved_firs) / max(fir_count, 1)
        if unresolved_ratio > 0.5:
            weight = 15.0
            score += weight
            factors.append(RiskFactor(name="Unresolved FIR Ratio", weight=weight, contribution=unresolved_ratio))

        hotspot_score = 0.0
        for c in entity_crimes:
            hotspot_score += 1.0
        if hotspot_score > 0:
            weight = min(hotspot_score * 1.5, 20.0)
            score += weight
            factors.append(RiskFactor(name="Hotspot Intensity", weight=weight, contribution=hotspot_score))

        repeat_offender_count = 0
        for criminal in criminals:
            if criminal.get("last_known_location") == entity_name:
                repeat_offender_count += 1
        if repeat_offender_count > 0:
            weight = min(repeat_offender_count * 3.0, 20.0)
            score += weight
            factors.append(RiskFactor(name="Repeat Offender Presence", weight=weight, contribution=repeat_offender_count))

        recent_crimes = 0
        now = datetime.now(timezone.utc)
        for c in entity_crimes:
            created = c.get("CREATEDTIME", "")
            if created:
                try:
                    dt = datetime.strptime(created[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    if (now - dt).days <= 30:
                        recent_crimes += 1
                except (ValueError, TypeError):
                    pass
        if recent_crimes > 0:
            weight = min(recent_crimes * 2.5, 15.0)
            score += weight
            factors.append(RiskFactor(name="Recent Crime Trend", weight=weight, contribution=recent_crimes))

        if score >= 70:
            level = "CRITICAL"
        elif score >= 50:
            level = "HIGH"
        elif score >= 25:
            level = "MEDIUM"
        else:
            level = "LOW"

        return score, factors, level
