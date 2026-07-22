from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from fastapi import Request
from app.repositories.report_repo import ReportRepository
from app.repositories.crime_repo import CrimeRepository
from app.repositories.fir_repo import FIRRepository
from app.repositories.hotspot_repo import HotspotRepository
from app.repositories.district_repo import DistrictRepository
from app.repositories.police_station_repo import PoliceStationRepository
from app.repositories.alert_repo import AlertRepository
from app.repositories.anomaly_repo import AnomalyRepository
from app.repositories.network_repo import NetworkRepository
from app.repositories.repeat_offender_repo import RepeatOffenderRepository
from app.repositories.predictive_risk_repo import PredictiveRiskRepository
from app.schemas.report import ReportType, ReportResponse, ReportSummaryResponse
from app.core.logger import logger
from app.core.exceptions import DataValidationError, RepositoryError

class ReportService:
    """Service layer for Report entity."""
    
    def __init__(self, request: Request, repo: ReportRepository):
        self.request = request
        self.repo = repo
        self.crime_repo = CrimeRepository(request)
        self.fir_repo = FIRRepository(request)
        self.hotspot_repo = HotspotRepository(request)
        self.district_repo = DistrictRepository(request)
        self.station_repo = PoliceStationRepository(request)
        self.alert_repo = AlertRepository(request)
        self.anomaly_repo = AnomalyRepository(request)
        self.network_repo = NetworkRepository(request)
        self.repeat_offender_repo = RepeatOffenderRepository(request)
        self.predictive_risk_repo = PredictiveRiskRepository(request)

    async def get_reports(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieves reports with pagination."""
        logger.info("Fetching Reports")
        return await self.repo.find_recent(limit=limit, offset=offset)

    async def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a report by ID."""
        logger.info(f"Fetching Report {report_id}")
        return await self.repo.find_by_id(report_id)

    async def get_summary(self) -> Dict[str, Any]:
        """Retrieves report summary counts."""
        logger.info("Fetching report summary")
        total = await self.repo.count()
        today = await self.repo.count_today()
        return {
            "total_reports": total,
            "reports_today": today,
            "available_report_types": len(ReportType),
        }

    async def get_statistics(self) -> Dict[str, Any]:
        """Retrieves report statistics."""
        logger.info("Fetching report statistics")
        reports = await self.repo.find_all(limit=1000)

        by_type: Dict[str, int] = {}
        by_status: Dict[str, int] = {}
        for r in reports:
            rt = r.get("report_type", "UNKNOWN")
            st = r.get("status", "ACTIVE")
            by_type[rt] = by_type.get(rt, 0) + 1
            by_status[st] = by_status.get(st, 0) + 1

        return {
            "by_type": [{"type": k, "count": v} for k, v in by_type.items()],
            "by_status": [{"status": k, "count": v} for k, v in by_status.items()],
            "total_count": len(reports),
        }

    async def get_report_types(self) -> List[Dict[str, str]]:
        """Returns available report types."""
        logger.info("Fetching report types")
        type_map = {
            ReportType.CRIME_SUMMARY: ("Crime Summary", "Aggregated crime statistics and trends"),
            ReportType.FIR_SUMMARY: ("FIR Summary", "FIR status and investigation metrics"),
            ReportType.HOTSPOT_ANALYSIS: ("Hotspot Analysis", "Geographic crime concentration analysis"),
            ReportType.REPEAT_OFFENDER_ANALYSIS: ("Repeat Offender Analysis", "Recidivism and repeat offence patterns"),
            ReportType.NETWORK_ANALYSIS: ("Network Analysis", "Criminal network and association mapping"),
            ReportType.PREDICTIVE_RISK: ("Predictive Risk", "Risk scoring and predictive indicators"),
            ReportType.ANOMALY_DETECTION: ("Anomaly Detection", "Statistical anomalies in crime patterns"),
            ReportType.ALERTS_SUMMARY: ("Alerts Summary", "Operational alerts and threshold breaches"),
            ReportType.DISTRICT_REPORT: ("District Report", "Per-district operational summary"),
            ReportType.STATION_REPORT: ("Station Report", "Per-station operational summary"),
        }
        return [
            {"type": t.value, "label": label, "description": desc}
            for t, (label, desc) in type_map.items()
        ]

    async def create_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new Report."""
        logger.info("Creating Report")
        if not data.get("name"):
            raise DataValidationError("Name is required")
        if not data.get("report_type"):
            raise DataValidationError("Report type is required")
        if not data.get("created_by_officer_id"):
            raise DataValidationError("Created by officer ID is required")
        result = await self.repo.create(data)
        logger.info("Report Created")
        return result

    async def delete_report(self, report_id: str) -> bool:
        """Deletes a Report."""
        logger.info(f"Deleting Report {report_id}")
        existing = await self.repo.find_by_id(report_id)
        if not existing:
            raise DataValidationError(f"Report {report_id} not found")
        result = await self.repo.delete(report_id)
        logger.info("Report Deleted")
        return result

    async def generate_report(self, report_type: str, officer_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generates a report deterministically from existing data."""
        parameters = parameters or {}
        report_type_enum = ReportType(report_type)

        generator = {
            ReportType.CRIME_SUMMARY: self._generate_crime_summary,
            ReportType.FIR_SUMMARY: self._generate_fir_summary,
            ReportType.HOTSPOT_ANALYSIS: self._generate_hotspot_analysis,
            ReportType.REPEAT_OFFENDER_ANALYSIS: self._generate_repeat_offender_analysis,
            ReportType.NETWORK_ANALYSIS: self._generate_network_analysis,
            ReportType.PREDICTIVE_RISK: self._generate_predictive_risk,
            ReportType.ANOMALY_DETECTION: self._generate_anomaly_detection,
            ReportType.ALERTS_SUMMARY: self._generate_alerts_summary,
            ReportType.DISTRICT_REPORT: self._generate_district_report,
            ReportType.STATION_REPORT: self._generate_station_report,
        }.get(report_type_enum)

        if not generator:
            raise DataValidationError(f"Unsupported report type: {report_type}")

        title, summary, statistics = await generator(parameters)

        report_data = {
            "name": parameters.get("name", title),
            "report_type": report_type,
            "parameters_json": str(parameters) if parameters else None,
            "created_by_officer_id": officer_id,
            "status": "ACTIVE",
        }

        created = await self.repo.create(report_data)
        report_id = created.get("ROWID", "")
        generated_at = created.get("CREATEDTIME", datetime.now(timezone.utc).isoformat())

        return {
            "report_id": report_id,
            "title": title,
            "type": report_type,
            "generated_at": generated_at,
            "generated_by": officer_id,
            "parameters": parameters,
            "summary": summary,
            "statistics": statistics,
        }

    async def _generate_crime_summary(self, parameters: Dict[str, Any]) -> tuple[str, str, Dict[str, Any]]:
        """Generates crime summary report."""
        crimes = await self.crime_repo.find_all(limit=1000)
        districts = await self.district_repo.find_active(limit=1000)

        by_type: Dict[str, int] = {}
        by_district: Dict[str, int] = {}
        by_status: Dict[str, int] = {}
        for c in crimes:
            ct = c.get("crime_type", "UNKNOWN")
            by_type[ct] = by_type.get(ct, 0) + 1
            did = c.get("district_id", "UNKNOWN")
            by_district[did] = by_district.get(did, 0) + 1
            st = c.get("status", "ACTIVE")
            by_status[st] = by_status.get(st, 0) + 1

        district_names = {d.get("ROWID", ""): d.get("name", "") for d in districts}

        summary = f"Total crimes: {len(crimes)} across {len(by_district)} districts"
        statistics = {
            "total_crimes": len(crimes),
            "by_type": [{"crime_type": k, "count": v} for k, v in sorted(by_type.items(), key=lambda x: x[1], reverse=True)],
            "by_district": [{"district_id": k, "district_name": district_names.get(k, k), "count": v} for k, v in sorted(by_district.items(), key=lambda x: x[1], reverse=True)],
            "by_status": [{"status": k, "count": v} for k, v in by_status.items()],
        }
        return "Crime Summary", summary, statistics

    async def _generate_fir_summary(self, parameters: Dict[str, Any]) -> tuple[str, str, Dict[str, Any]]:
        """Generates FIR summary report."""
        firs = await self.fir_repo.find_all(limit=1000)
        stations = await self.station_repo.find_active(limit=1000)

        by_status: Dict[str, int] = {}
        by_station: Dict[str, int] = {}
        for f in firs:
            st = f.get("status", "ACTIVE")
            by_status[st] = by_status.get(st, 0) + 1
            sid = f.get("station_id", "UNKNOWN")
            by_station[sid] = by_station.get(sid, 0) + 1

        station_names = {s.get("ROWID", ""): s.get("name", "") for s in stations}

        summary = f"Total FIRs: {len(firs)} across {len(by_station)} stations"
        statistics = {
            "total_firs": len(firs),
            "by_status": [{"status": k, "count": v} for k, v in by_status.items()],
            "by_station": [{"station_id": k, "station_name": station_names.get(k, k), "count": v} for k, v in sorted(by_station.items(), key=lambda x: x[1], reverse=True)],
        }
        return "FIR Summary", summary, statistics

    async def _generate_hotspot_analysis(self, parameters: Dict[str, Any]) -> tuple[str, str, Dict[str, Any]]:
        """Generates hotspot analysis report."""
        hotspots = await self.hotspot_repo.find_all(limit=1000)
        districts = await self.district_repo.find_active(limit=1000)

        district_map: Dict[str, Dict[str, Any]] = {}
        for h in hotspots:
            did = h.get("district_id", "UNKNOWN")
            if did not in district_map:
                district_map[did] = {"crime_count": 0, "hotspot_score": 0.0}
            district_map[did]["crime_count"] += h.get("crime_count", 0)
            district_map[did]["hotspot_score"] += h.get("hotspot_score", 0.0)

        district_names = {d.get("ROWID", ""): d.get("name", "") for d in districts}

        summary = f"Total hotspots: {len(hotspots)} across {len(district_map)} districts"
        statistics = {
            "total_hotspots": len(hotspots),
            "by_district": [
                {
                    "district_id": k,
                    "district_name": district_names.get(k, k),
                    "crime_count": v["crime_count"],
                    "average_hotspot_score": round(v["hotspot_score"] / max(len(hotspots), 1), 2),
                }
                for k, v in sorted(district_map.items(), key=lambda x: x[1]["crime_count"], reverse=True)
            ],
        }
        return "Hotspot Analysis", summary, statistics

    async def _generate_repeat_offender_analysis(self, parameters: Dict[str, Any]) -> tuple[str, str, Dict[str, Any]]:
        """Generates repeat offender analysis report."""
        offenders = await self.repeat_offender_repo.find_active(limit=1000)
        districts = await self.district_repo.find_active(limit=1000)

        district_counts: Dict[str, int] = {}
        for o in offenders:
            for d in o.get("districts_involved", []):
                district_counts[d] = district_counts.get(d, 0) + 1

        district_names = {d.get("ROWID", ""): d.get("name", "") for d in districts}

        summary = f"Total repeat offenders: {len(offenders)}"
        statistics = {
            "total_repeat_offenders": len(offenders),
            "by_district": [
                {"district_id": k, "district_name": district_names.get(k, k), "count": v}
                for k, v in sorted(district_counts.items(), key=lambda x: x[1], reverse=True)
            ],
        }
        return "Repeat Offender Analysis", summary, statistics

    async def _generate_network_analysis(self, parameters: Dict[str, Any]) -> tuple[str, str, Dict[str, Any]]:
        """Generates network analysis report."""
        nodes = await self.network_repo.find_all_nodes(limit=1000)
        edges = await self.network_repo.find_all_edges(limit=1000)

        summary = f"Network contains {len(nodes)} nodes and {len(edges)} edges"
        statistics = {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "node_types": {},
            "edge_types": {},
        }
        for n in nodes:
            nt = n.get("node_type", "UNKNOWN")
            statistics["node_types"][nt] = statistics["node_types"].get(nt, 0) + 1
        for e in edges:
            et = e.get("edge_type", "UNKNOWN")
            statistics["edge_types"][et] = statistics["edge_types"].get(et, 0) + 1
        return "Network Analysis", summary, statistics

    async def _generate_predictive_risk(self, parameters: Dict[str, Any]) -> tuple[str, str, Dict[str, Any]]:
        """Generates predictive risk report."""
        risks = await self.predictive_risk_repo.find_all(limit=1000)
        districts = await self.district_repo.find_active(limit=1000)

        district_map: Dict[str, List[Dict[str, Any]]] = {}
        for r in risks:
            did = r.get("district_id", "UNKNOWN")
            district_map.setdefault(did, []).append(r)

        district_names = {d.get("ROWID", ""): d.get("name", "") for d in districts}

        summary = f"Total risk predictions: {len(risks)}"
        statistics = {
            "total_predictions": len(risks),
            "by_district": [
                {
                    "district_id": k,
                    "district_name": district_names.get(k, k),
                    "prediction_count": len(v),
                    "average_risk_score": round(sum(item.get("risk_score", 0) for item in v) / max(len(v), 1), 2),
                }
                for k, v in sorted(district_map.items(), key=lambda x: len(x[1]), reverse=True)
            ],
        }
        return "Predictive Risk", summary, statistics

    async def _generate_anomaly_detection(self, parameters: Dict[str, Any]) -> tuple[str, str, Dict[str, Any]]:
        """Generates anomaly detection report."""
        anomalies = await self.anomaly_repo.find_all(limit=1000)
        districts = await self.district_repo.find_active(limit=1000)

        by_severity: Dict[str, int] = {}
        by_district: Dict[str, int] = {}
        for a in anomalies:
            sev = a.get("severity", "UNKNOWN")
            by_severity[sev] = by_severity.get(sev, 0) + 1
            did = a.get("affected_entity_id", "UNKNOWN")
            by_district[did] = by_district.get(did, 0) + 1

        district_names = {d.get("ROWID", ""): d.get("name", "") for d in districts}

        summary = f"Total anomalies detected: {len(anomalies)}"
        statistics = {
            "total_anomalies": len(anomalies),
            "by_severity": [{"severity": k, "count": v} for k, v in sorted(by_severity.items())],
            "by_district": [
                {"district_id": k, "district_name": district_names.get(k, k), "count": v}
                for k, v in sorted(by_district.items(), key=lambda x: x[1], reverse=True)
            ],
        }
        return "Anomaly Detection", summary, statistics

    async def _generate_alerts_summary(self, parameters: Dict[str, Any]) -> tuple[str, str, Dict[str, Any]]:
        """Generates alerts summary report."""
        alerts = await self.alert_repo.find_all(limit=1000)
        districts = await self.district_repo.find_active(limit=1000)

        by_status: Dict[str, int] = {}
        by_severity: Dict[str, int] = {}
        by_district: Dict[str, int] = {}
        for a in alerts:
            st = a.get("status", "ACTIVE")
            by_status[st] = by_status.get(st, 0) + 1
            sev = a.get("severity", "UNKNOWN")
            by_severity[sev] = by_severity.get(sev, 0) + 1
            did = a.get("district_id", "UNKNOWN")
            if did:
                by_district[did] = by_district.get(did, 0) + 1

        district_names = {d.get("ROWID", ""): d.get("name", "") for d in districts}

        summary = f"Total alerts: {len(alerts)}"
        statistics = {
            "total_alerts": len(alerts),
            "by_status": [{"status": k, "count": v} for k, v in by_status.items()],
            "by_severity": [{"severity": k, "count": v} for k, v in sorted(by_severity.items())],
            "by_district": [
                {"district_id": k, "district_name": district_names.get(k, k), "count": v}
                for k, v in sorted(by_district.items(), key=lambda x: x[1], reverse=True)
            ],
        }
        return "Alerts Summary", summary, statistics

    async def _generate_district_report(self, parameters: Dict[str, Any]) -> tuple[str, str, Dict[str, Any]]:
        """Generates district report."""
        district_id = parameters.get("district_id")
        districts = await self.district_repo.find_all(limit=1000)
        target = next((d for d in districts if d.get("ROWID") == district_id), None)

        if not target:
            target = districts[0] if districts else {}
            district_id = target.get("ROWID", "")

        crimes = await self.crime_repo.find_by_district(district_id, limit=1000)
        firs = await self.fir_repo.find_all_with_filters(district_id=district_id, limit=1000)
        alerts = await self.alert_repo.find_by_district(district_id, limit=1000)

        by_crime_type: Dict[str, int] = {}
        for c in crimes:
            ct = c.get("crime_type", "UNKNOWN")
            by_crime_type[ct] = by_crime_type.get(ct, 0) + 1

        summary = f"District {target.get('name', district_id)}: {len(crimes)} crimes, {len(firs)} FIRs, {len(alerts)} alerts"
        statistics = {
            "district_id": district_id,
            "district_name": target.get("name", ""),
            "total_crimes": len(crimes),
            "total_firs": len(firs),
            "total_alerts": len(alerts),
            "by_crime_type": [{"crime_type": k, "count": v} for k, v in sorted(by_crime_type.items(), key=lambda x: x[1], reverse=True)],
        }
        return f"District Report - {target.get('name', district_id)}", summary, statistics

    async def _generate_station_report(self, parameters: Dict[str, Any]) -> tuple[str, str, Dict[str, Any]]:
        """Generates station report."""
        station_id = parameters.get("station_id")
        stations = await self.station_repo.find_all(limit=1000)
        target = next((s for s in stations if s.get("ROWID") == station_id), None)

        if not target:
            target = stations[0] if stations else {}
            station_id = target.get("ROWID", "")

        crimes = await self.crime_repo.find_by_station(station_id, limit=1000)
        firs = await self.fir_repo.find_by_station(station_id, limit=1000)
        alerts = await self.alert_repo.find_by_district(target.get("district_id", ""), limit=1000)

        by_crime_type: Dict[str, int] = {}
        for c in crimes:
            ct = c.get("crime_type", "UNKNOWN")
            by_crime_type[ct] = by_crime_type.get(ct, 0) + 1

        summary = f"Station {target.get('name', station_id)}: {len(crimes)} crimes, {len(firs)} FIRs"
        statistics = {
            "station_id": station_id,
            "station_name": target.get("name", ""),
            "district_id": target.get("district_id", ""),
            "total_crimes": len(crimes),
            "total_firs": len(firs),
            "by_crime_type": [{"crime_type": k, "count": v} for k, v in sorted(by_crime_type.items(), key=lambda x: x[1], reverse=True)],
        }
        return f"Station Report - {target.get('name', station_id)}", summary, statistics
