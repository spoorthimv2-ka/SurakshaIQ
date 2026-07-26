from typing import Any, Dict, List, Optional
from datetime import datetime, timezone, timedelta
from fastapi import Request

from app.repositories.anomaly_repo import AnomalyRepository
from app.repositories.crime_repo import CrimeRepository
from app.repositories.fir_repo import FIRRepository
from app.repositories.district_repo import DistrictRepository
from app.repositories.police_station_repo import PoliceStationRepository
from app.repositories.hotspot_repo import HotspotRepository
from app.repositories.repeat_offender_repo import RepeatOffenderRepository
from app.repositories.prediction_ledger_repo import PredictionLedgerRepository
from app.core.logger import logger
from app.core.utils import catalyst_datetime
from app.schemas.anomaly import (
    Anomaly,
    AnomalyFactor,
    AnomalySummary,
    DistrictAnomaly,
    StationAnomaly,
)


class AnomalyService:
    """Service layer for anomaly detection."""

    def __init__(self, request: Request):
        self.request = request
        self.repo = AnomalyRepository(request)
        self.crime_repo = CrimeRepository(request)
        self.fir_repo = FIRRepository(request)
        self.district_repo = DistrictRepository(request)
        self.station_repo = PoliceStationRepository(request)
        self.hotspot_repo = HotspotRepository(request)
        self.repeat_offender_repo = RepeatOffenderRepository(request)

    async def _record_ledger(self, entity_type: str, entity_id: str, score: float, level: str, factors: Optional[List[Dict[str, Any]]] = None, prediction_type: Optional[str] = None) -> None:
        try:
            repo = PredictionLedgerRepository(self.request)
            await repo.record({
                "entity_type": entity_type,
                "entity_id": entity_id,
                "entity_name": entity_id,
                "prediction_type": prediction_type or "ANOMALY",
                "score": score,
                "level": level,
                "factors": factors or [],
                "model_version": "v1-heuristic",
                "scored_at": catalyst_datetime(),
            })
        except Exception as e:
            logger.warning(f"Ledger write failed: {e}")

    async def get_anomalies(self, officer: Dict[str, Any], limit: int = 100) -> List[Anomaly]:
        """Retrieves detected anomalies for all districts and stations."""
        
        data = await self.repo.get_anomaly_data(limit=limit)
        anomalies: List[Anomaly] = []

        for district in data.get("districts", []):
            did = district.get("ROWID", district.get("id", ""))
            dname = district.get("name", did)
            entity_anomalies = self._detect_entity_anomalies(data, did, "District", dname)
            anomalies.extend(entity_anomalies)

        for station in data.get("stations", []):
            sid = station.get("ROWID", station.get("id", ""))
            sname = station.get("name", sid)
            did = station.get("district_id", "UNKNOWN")
            entity_anomalies = self._detect_entity_anomalies(data, sid, "PoliceStation", sname, parent_id=did)
            anomalies.extend(entity_anomalies)

        anomalies.sort(key=lambda x: x.anomaly_score, reverse=True)
        result = anomalies[:limit]
        for a in result:
            await self._record_ledger(a.affected_entity_type, a.affected_entity_id, a.anomaly_score, a.severity, [f.model_dump(mode="json") for f in a.contributing_factors])
        return result

    async def get_summary(self, officer: Dict[str, Any]) -> AnomalySummary:
        """Retrieves aggregated anomaly summary."""
        
        anomalies = await self.get_anomalies(officer, limit=1000)
        high = [a for a in anomalies if a.severity == "HIGH"]
        critical = [a for a in anomalies if a.severity == "CRITICAL"]
        affected_districts = len({a.affected_entity_id for a in anomalies if a.affected_entity_type == "District"})
        affected_stations = len({a.affected_entity_id for a in anomalies if a.affected_entity_type == "PoliceStation"})
        avg_score = sum(a.anomaly_score for a in anomalies) / max(len(anomalies), 1)

        distribution = [
            {
                "anomaly_id": a.anomaly_id,
                "anomaly_type": a.anomaly_type,
                "severity": a.severity,
                "affected_entity_id": a.affected_entity_id,
                "affected_entity_type": a.affected_entity_type,
                "affected_entity_name": a.affected_entity_name,
                "anomaly_score": a.anomaly_score,
            }
            for a in anomalies
        ]

        summary = AnomalySummary(
            total_anomalies=len(anomalies),
            high_anomalies=len(high),
            critical_anomalies=len(critical),
            affected_districts=affected_districts,
            affected_stations=affected_stations,
            average_anomaly_score=round(avg_score, 2),
            anomaly_distribution=distribution,
        )
        await self._record_ledger("Summary", "anomaly-summary", round(avg_score, 2), "LOW", prediction_type="ANOMALY_SUMMARY")
        return summary

    async def get_district_anomalies(self, officer: Dict[str, Any]) -> List[DistrictAnomaly]:
        """Retrieves anomalies for all districts."""
        
        anomalies = await self.get_anomalies(officer, limit=1000)
        district_data: Dict[str, Dict[str, Any]] = {}

        for a in anomalies:
            if a.affected_entity_type != "District":
                continue
            did = a.affected_entity_id
            if did not in district_data:
                district_data[did] = {
                    "district_name": a.affected_entity_name,
                    "anomaly_score": 0,
                    "severity": "LOW",
                    "crime_count": 0,
                    "fir_count": 0,
                    "hotspot_score": 0.0,
                    "contributing_factors": [],
                }
            d = district_data[did]
            d["anomaly_score"] += a.anomaly_score
            d["contributing_factors"].extend(a.contributing_factors)
            if {"CRITICAL", "HIGH", "MEDIUM", "LOW"}.index(a.severity) > {"CRITICAL", "HIGH", "MEDIUM", "LOW"}.index(d["severity"]):
                d["severity"] = a.severity

        data = await self.repo.get_anomaly_data(limit=2000)
        crimes = data.get("crimes", [])
        firs_data = data.get("firs", [])
        for did, d in district_data.items():
            entity_crimes = [c for c in crimes if c.get("district_id") == did]
            entity_firs = [f for f in firs_data if f.get("district_id") == did]
            d["crime_count"] = len(entity_crimes)
            d["fir_count"] = len(entity_firs)
            d["hotspot_score"] = round(self._check_hotspot_intensity(entity_crimes), 2)

        return [
            DistrictAnomaly(
                district_id=did,
                district_name=d["district_name"],
                anomaly_score=round(d["anomaly_score"], 2),
                severity=d["severity"],
                crime_count=d["crime_count"],
                fir_count=d["fir_count"],
                hotspot_score=d["hotspot_score"],
                contributing_factors=d["contributing_factors"],
            )
            for did, d in district_data.items()
        ]

    async def get_station_anomalies(self, officer: Dict[str, Any]) -> List[StationAnomaly]:
        """Retrieves anomalies for all police stations."""
        
        anomalies = await self.get_anomalies(officer, limit=1000)
        station_data: Dict[str, Dict[str, Any]] = {}

        for a in anomalies:
            if a.affected_entity_type != "PoliceStation":
                continue
            sid = a.affected_entity_id
            did = a.affected_entity_id
            if sid not in station_data:
                station_data[sid] = {
                    "station_name": a.affected_entity_name,
                    "district_id": "",
                    "district_name": "",
                    "anomaly_score": 0,
                    "severity": "LOW",
                    "crime_count": 0,
                    "fir_count": 0,
                    "hotspot_score": 0.0,
                    "contributing_factors": [],
                }
            s = station_data[sid]
            s["anomaly_score"] += a.anomaly_score
            s["contributing_factors"].extend(a.contributing_factors)
            if {"CRITICAL", "HIGH", "MEDIUM", "LOW"}.index(a.severity) > {"CRITICAL", "HIGH", "MEDIUM", "LOW"}.index(s["severity"]):
                s["severity"] = a.severity

        data = await self.repo.get_anomaly_data(limit=2000)
        crimes = data.get("crimes", [])
        firs_data = data.get("firs", [])
        for sid, s in station_data.items():
            entity_crimes = [c for c in crimes if c.get("station_id") == sid]
            entity_firs = [f for f in firs_data if f.get("station_id") == sid]
            s["crime_count"] = len(entity_crimes)
            s["fir_count"] = len(entity_firs)
            s["hotspot_score"] = round(self._check_hotspot_intensity(entity_crimes), 2)

        return [
            StationAnomaly(
                station_id=sid,
                station_name=s["station_name"],
                district_id=s["district_id"],
                district_name=s["district_name"],
                anomaly_score=round(s["anomaly_score"], 2),
                severity=s["severity"],
                crime_count=s["crime_count"],
                fir_count=s["fir_count"],
                hotspot_score=s["hotspot_score"],
                contributing_factors=s["contributing_factors"],
            )
            for sid, s in station_data.items()
        ]

    async def get_anomaly(self, officer: Dict[str, Any], anomaly_id: str) -> Optional[Anomaly]:
        """Retrieves a specific anomaly by ID."""
        
        anomalies = await self.get_anomalies(officer, limit=1000)
        for a in anomalies:
            if a.anomaly_id == anomaly_id:
                return a
        return None

    def _detect_entity_anomalies(
        self,
        data: Dict[str, Any],
        entity_id: str,
        entity_type: str,
        entity_name: str,
        parent_id: Optional[str] = None,
    ) -> List[Anomaly]:
        """Detects anomalies for a specific entity using deterministic rules."""
        anomalies: List[Anomaly] = []
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
            score, factors, level = self._check_crime_spike(data, entity_id, entity_type, crime_count)
            if score > 0:
                anomalies.append(
                    Anomaly(
                        anomaly_id=f"ANOMALY-{entity_type}-{entity_id}-CRIME_SPIKE",
                        anomaly_type="CRIME_SPIKE",
                        severity=level,
                        affected_entity_id=entity_id,
                        affected_entity_type=entity_type,
                        affected_entity_name=entity_name,
                        anomaly_score=score,
                        contributing_factors=factors,
                        description=f"Unusual crime spike detected for {entity_name}. Count: {crime_count}.",
                        detected_at=datetime.now(timezone.utc).isoformat(),
                    )
                )

        if fir_count > 0:
            score, factors, level = self._check_fir_spike(entity_firs, fir_count)
            if score > 0:
                anomalies.append(
                    Anomaly(
                        anomaly_id=f"ANOMALY-{entity_type}-{entity_id}-FIR_SPIKE",
                        anomaly_type="FIR_SPIKE",
                        severity=level,
                        affected_entity_id=entity_id,
                        affected_entity_type=entity_type,
                        affected_entity_name=entity_name,
                        anomaly_score=score,
                        contributing_factors=factors,
                        description=f"Unusual FIR spike detected for {entity_name}. Count: {fir_count}.",
                        detected_at=datetime.now(timezone.utc).isoformat(),
                    )
                )

        hotspot_score = self._check_hotspot_intensity(entity_crimes)
        if hotspot_score > 0:
            anomalies.append(
                Anomaly(
                    anomaly_id=f"ANOMALY-{entity_type}-{entity_id}-HOTSPOT",
                    anomaly_type="HOTSPOT_INTENSITY",
                    severity="HIGH" if hotspot_score >= 70 else "MEDIUM",
                    affected_entity_id=entity_id,
                    affected_entity_type=entity_type,
                    affected_entity_name=entity_name,
                    anomaly_score=hotspot_score,
                    contributing_factors=[AnomalyFactor(name="Hotspot Intensity", weight=hotspot_score, contribution=hotspot_score)],
                    description=f"Abnormal hotspot intensity detected for {entity_name}.",
                    detected_at=datetime.now(timezone.utc).isoformat(),
                )
            )

        repeat_score = self._check_repeat_offender_activity(criminals, entity_id, entity_type)
        if repeat_score > 0:
            anomalies.append(
                Anomaly(
                    anomaly_id=f"ANOMALY-{entity_type}-{entity_id}-REPEAT_OFFENDER",
                    anomaly_type="REPEAT_OFFENDER_ACTIVITY",
                    severity="HIGH" if repeat_score >= 50 else "MEDIUM",
                    affected_entity_id=entity_id,
                    affected_entity_type=entity_type,
                    affected_entity_name=entity_name,
                    anomaly_score=repeat_score,
                    contributing_factors=[AnomalyFactor(name="Repeat Offender Activity", weight=repeat_score, contribution=repeat_score)],
                    description=f"Unusual repeat offender activity detected for {entity_name}.",
                    detected_at=datetime.now(timezone.utc).isoformat(),
                )
            )

        return anomalies

    def _check_crime_spike(self, data: Dict[str, Any], entity_id: str, entity_type: str, crime_count: int) -> tuple[float, List[AnomalyFactor], str]:
        """Detects crime spike anomalies."""
        factors: List[AnomalyFactor] = []
        score = 0.0

        if crime_count >= 20:
            score = 80.0
            factors.append(AnomalyFactor(name="Severe Crime Frequency", weight=80.0, contribution=crime_count))
            level = "CRITICAL"
        elif crime_count >= 10:
            score = 60.0
            factors.append(AnomalyFactor(name="High Crime Frequency", weight=60.0, contribution=crime_count))
            level = "HIGH"
        elif crime_count >= 5:
            score = 40.0
            factors.append(AnomalyFactor(name="Elevated Crime Frequency", weight=40.0, contribution=crime_count))
            level = "MEDIUM"
        else:
            level = "LOW"

        return score, factors, level

    def _check_fir_spike(self, firs: List[Dict[str, Any]], fir_count: int) -> tuple[float, List[AnomalyFactor], str]:
        """Detects FIR spike anomalies."""
        factors: List[AnomalyFactor] = []
        score = 0.0

        active_firs = [f for f in firs if f.get("status") == "ACTIVE"]
        unresolved_ratio = len(active_firs) / max(fir_count, 1)

        if fir_count >= 20 and unresolved_ratio >= 0.7:
            score = 70.0
            factors.append(AnomalyFactor(name="Critical FIR Volume", weight=70.0, contribution=fir_count))
            level = "CRITICAL"
        elif fir_count >= 10 and unresolved_ratio >= 0.5:
            score = 50.0
            factors.append(AnomalyFactor(name="High FIR Volume", weight=50.0, contribution=fir_count))
            level = "HIGH"
        elif fir_count >= 5:
            score = 30.0
            factors.append(AnomalyFactor(name="Elevated FIR Volume", weight=30.0, contribution=fir_count))
            level = "MEDIUM"
        else:
            level = "LOW"

        return score, factors, level

    def _check_hotspot_intensity(self, crimes: List[Dict[str, Any]]) -> float:
        """Checks hotspot intensity."""
        if not crimes:
            return 0.0
        count = len(crimes)
        if count >= 30:
            return 60.0
        if count >= 15:
            return 40.0
        if count >= 5:
            return 20.0
        return min(count * 3.0, 15.0)

    def _check_repeat_offender_activity(self, criminals: List[Dict[str, Any]], entity_id: str, entity_type: str) -> float:
        """Checks repeat offender activity."""
        count = 0
        for criminal in criminals:
            location = criminal.get("last_known_location", "")
            if entity_type == "District" and location == entity_id:
                count += 1
            elif entity_type == "PoliceStation" and criminal.get("ROWID", "").endswith(entity_id.split("-")[-1]):
                count += 1
        return min(count * 3.0, 30.0)
