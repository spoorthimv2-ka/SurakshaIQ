from typing import Any, Dict, List, Optional
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from fastapi import Request
import traceback

from app.repositories.predictive_repo import PredictiveRepository
from app.repositories.crime_repo import CrimeRepository
from app.repositories.fir_repo import FIRRepository
from app.repositories.hotspot_repo import HotspotRepository
from app.repositories.district_repo import DistrictRepository
from app.repositories.police_station_repo import PoliceStationRepository
from app.repositories.repeat_offender_repo import RepeatOffenderRepository
from app.repositories.prediction_ledger_repo import PredictionLedgerRepository
from app.services.ai.fallback_executive_intelligence import generate_local_explanation
from app.services.ai_service import ExecutiveIntelligenceService
from app.core.logger import logger
from app.schemas.predictive import (
    CrimeForecast,
    ForecastPoint,
    EmergingHotspot,
    RiskIndex,
    PatrolRecommendation,
    TemporalIntelligence,
    TemporalDistribution,
    TrendAnalysis,
    TrendCategory,
    EmergingPattern,
    ScenarioSimulation,
    ScenarioFilters,
    PredictiveDashboard,
    PredictiveAIExplanation,
    PredictiveFilters,
)


class PredictiveService:
    """Service layer for predictive intelligence."""

    def __init__(self, request: Request):
        self.request = request
        self.repo = PredictiveRepository(request)
        self.crime_repo = CrimeRepository(request)
        self.fir_repo = FIRRepository(request)
        self.hotspot_repo = HotspotRepository(request)
        self.district_repo = DistrictRepository(request)
        self.station_repo = PoliceStationRepository(request)
        self.repeat_offender_repo = RepeatOffenderRepository(request)

    async def _record_ledger(self, entity_type: str, entity_id: str, score: float, level: str, prediction_type: str = "PREDICTIVE") -> None:
        try:
            repo = PredictionLedgerRepository(self.request)
            await repo.record({
                "entity_type": entity_type,
                "entity_id": entity_id,
                "entity_name": entity_id,
                "prediction_type": prediction_type,
                "score": score,
                "level": level,
                "factors": [],
                "model_version": "v1-heuristic",
                "scored_at": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as e:
            logger.warning(f"Ledger write failed: {e}")

    async def get_forecast(self, officer: Dict[str, Any], filters: Optional[PredictiveFilters] = None) -> List[CrimeForecast]:
        data = await self.repo.get_predictive_data(limit=2000)
        crimes = data.get("crimes", [])
        filters = filters or PredictiveFilters()

        period_map = {"7d": 7, "30d": 30, "quarter": 90}
        days = period_map.get(filters.time_period or "30d", 30)
        now = datetime.now(timezone.utc)

        entity_crimes: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for c in crimes:
            cid = c.get("district_id", "") or c.get("station_id", "") or "ALL"
            if filters.district_id and c.get("district_id") != filters.district_id:
                continue
            if filters.station_id and c.get("station_id") != filters.station_id:
                continue
            if filters.crime_category and c.get("crime_type") != filters.crime_category:
                continue
            entity_crimes[cid].append(c)

        forecasts: List[CrimeForecast] = []
        for entity_id, ecrimes in entity_crimes.items():
            etype = "District" if filters.district_id else ("PoliceStation" if filters.station_id else "District")
            ename = entity_id
            district_obj = next((d for d in data.get("districts", []) if d.get("ROWID") == entity_id), None)
            if district_obj:
                ename = district_obj.get("name", entity_id)
            station_obj = next((s for s in data.get("stations", []) if s.get("ROWID") == entity_id), None)
            if station_obj:
                ename = station_obj.get("name", entity_id)

            future_dates = [(now + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
            points: List[ForecastPoint] = []
            total = 0
            for fd in future_dates:
                base = len(ecrimes) / max(days, 1)
                day_of_week = datetime.strptime(fd, "%Y-%m-%d").weekday()
                seasonal = 1.0 + 0.1 * ((int(fd[:4]) - 2022) % 3)
                predicted = max(0, int(base * seasonal * (1 + 0.05 * (day_of_week % 3))))
                low = max(0, predicted - max(1, int(predicted * 0.2)))
                high = predicted + max(1, int(predicted * 0.2))
                confidence = min(0.95, 0.6 + 0.01 * len(ecrimes))
                points.append(ForecastPoint(
                    date=fd,
                    predicted_count=predicted,
                    confidence_low=low,
                    confidence_high=high,
                    confidence_score=round(confidence, 2),
                ))
                total += predicted

            forecasts.append(CrimeForecast(
                entity_id=entity_id,
                entity_type=etype,
                entity_name=ename,
                period=f"next_{days}_days",
                forecast_points=points,
                confidence=round(sum(p.confidence_score for p in points) / max(len(points), 1), 2),
                total_predicted=total,
            ))

        return forecasts

    async def get_emerging_hotspots(self, officer: Dict[str, Any], filters: Optional[PredictiveFilters] = None) -> List[EmergingHotspot]:
        data = await self.repo.get_predictive_data(limit=2000)
        crimes = data.get("crimes", [])
        filters = filters or PredictiveFilters()

        district_counts: Dict[str, int] = defaultdict(int)
        district_recent: Dict[str, int] = defaultdict(int)
        now = datetime.now(timezone.utc)
        recent_cutoff = now - timedelta(days=7)

        for c in crimes:
            did = c.get("district_id", "UNKNOWN")
            district_counts[did] += 1
            created = c.get("CREATEDTIME", "")
            if created:
                try:
                    dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    if dt >= recent_cutoff:
                        district_recent[did] += 1
                except Exception as exception:
                    logger.warning("Failed to parse created timestamp: %s\n%s", exception, traceback.format_exc())

        hotspots: List[EmergingHotspot] = []
        for did, total in district_counts.items():
            recent = district_recent.get(did, 0)
            intensity = round(recent / max(total, 1), 3)
            if intensity <= 0:
                continue
            district_obj = next((d for d in data.get("districts", []) if d.get("ROWID") == did), {})
            dname = district_obj.get("name", did)
            station_obj = next((s for s in data.get("stations", []) if s.get("district_id") == did), {})
            sid = station_obj.get("ROWID", "")
            sname = station_obj.get("name", sid)
            confidence = min(0.95, 0.5 + 0.05 * recent + 0.02 * total)
            risk = "High" if confidence > 0.7 else ("Medium" if confidence > 0.4 else "Low")
            explanation = f"Crime density increased by {round(intensity * 100, 1)}% in the last 7 days. {recent} recent incidents out of {total} historical."
            hotspots.append(EmergingHotspot(
                id=f"EHOT-{did}",
                district_id=did,
                district_name=dname,
                station_id=sid,
                station_name=sname,
                intensity=round(intensity, 3),
                confidence=round(confidence, 2),
                risk_level=risk,
                explanation=explanation,
                predicted_crime_count=recent,
            ))

        hotspots.sort(key=lambda x: x.intensity, reverse=True)
        return hotspots[:20]

    async def get_dynamic_risk_index(self, officer: Dict[str, Any], filters: Optional[PredictiveFilters] = None) -> List[RiskIndex]:
        data = await self.repo.get_predictive_data(limit=2000)
        crimes = data.get("crimes", [])
        firs = data.get("firs", [])
        hotspots = data.get("hotspots", [])
        criminals = data.get("criminals", [])
        filters = filters or PredictiveFilters()

        hotspot_map: Dict[str, float] = defaultdict(float)
        for h in hotspots:
            did = h.get("district_id", "")
            hotspot_map[did] += h.get("crime_count", 0)

        repeat_map: Dict[str, int] = defaultdict(int)
        for c in criminals:
            rid = c.get("ROWID", "")
            if rid:
                repeat_map[rid] += 1

        district_data: Dict[str, Dict[str, Any]] = {}
        for c in crimes:
            did = c.get("district_id", "UNKNOWN")
            if filters.district_id and did != filters.district_id:
                continue
            if filters.crime_category and c.get("crime_type") != filters.crime_category:
                continue
            if did not in district_data:
                district_data[did] = {"crimes": 0, "firs": 0, "hotspot": 0.0, "repeat": 0}
            district_data[did]["crimes"] += 1

        for f in firs:
            did = f.get("district_id", "UNKNOWN")
            if filters.district_id and did != filters.district_id:
                continue
            if did not in district_data:
                district_data[did] = {"crimes": 0, "firs": 0, "hotspot": 0.0, "repeat": 0}
            district_data[did]["firs"] += 1

        for did, hscore in hotspot_map.items():
            if did in district_data:
                district_data[did]["hotspot"] = hscore

        for rid, rcount in repeat_map.items():
            for did in district_data:
                district_data[did]["repeat"] += rcount

        results: List[RiskIndex] = []
        for did, d in district_data.items():
            district_obj = next((dobj for dobj in data.get("districts", []) if dobj.get("ROWID") == did), {})
            dname = district_obj.get("name", did)
            score = (
                d["crimes"] * 2.0
                + d["firs"] * 1.0
                + d["hotspot"] * 1.5
                + d["repeat"] * 3.0
            )
            previous_score = round(score * 0.85, 2)
            change = round(score - previous_score, 2)
            trend = "increasing" if change > 0 else "decreasing" if change < 0 else "stable"
            risk = "Critical" if score >= 50 else "High" if score >= 25 else "Medium" if score >= 10 else "Low"
            explanation = f"Based on {d['crimes']} crimes, {d['firs']} FIRs, hotspot score {round(d['hotspot'], 1)}, and repeat offender presence. Risk trend is {trend}."
            results.append(RiskIndex(
                entity_id=did,
                entity_type="District",
                entity_name=dname,
                risk_score=round(score, 2),
                risk_level=risk,
                trend=trend,
                previous_score=previous_score,
                score_change=change,
                explanation=explanation,
            ))

        results.sort(key=lambda x: x.risk_score, reverse=True)
        return results

    async def get_patrol_recommendations(self, officer: Dict[str, Any], filters: Optional[PredictiveFilters] = None) -> List[PatrolRecommendation]:
        risk_indices = await self.get_dynamic_risk_index(officer, filters)
        hotspots = await self.get_emerging_hotspots(officer, filters)
        filters = filters or PredictiveFilters()

        recs: List[PatrolRecommendation] = []
        for risk in risk_indices:
            if risk.risk_score >= 25:
                recs.append(PatrolRecommendation(
                    zone_id=risk.entity_id,
                    zone_name=risk.entity_name,
                    zone_type=risk.entity_type,
                    recommendation_type="patrol_allocation",
                    priority=risk.risk_level,
                    description=f"Increase patrol presence in {risk.entity_name} due to rising risk score ({risk.risk_score}).",
                    reason=risk.explanation,
                    suggested_patrols=max(1, int(risk.risk_score / 10)),
                    time_windows=["18:00-22:00", "22:00-04:00"] if risk.risk_level in ("High", "Critical") else ["09:00-18:00"],
                ))

        for hs in hotspots[:5]:
            existing = [r for r in recs if r.zone_id == hs.district_id]
            if not existing:
                recs.append(PatrolRecommendation(
                    zone_id=hs.district_id,
                    zone_name=hs.district_name,
                    zone_type="District",
                    recommendation_type="surveillance",
                    priority=hs.risk_level,
                    description=f"Deploy surveillance to emerging hotspot {hs.district_name}.",
                    reason=hs.explanation,
                    suggested_patrols=2,
                    time_windows=["18:00-22:00"],
                ))

        return recs

    async def get_temporal_intelligence(self, officer: Dict[str, Any], filters: Optional[PredictiveFilters] = None) -> TemporalIntelligence:
        data = await self.repo.get_predictive_data(limit=2000)
        crimes = data.get("crimes", [])
        filters = filters or PredictiveFilters()

        hourly: Dict[int, int] = defaultdict(int)
        daily: Dict[str, int] = defaultdict(int)
        monthly: Dict[str, int] = defaultdict(int)
        seasonal: Dict[str, int] = defaultdict(int)
        total = 0

        for c in crimes:
            created = c.get("CREATEDTIME", "")
            if not created:
                continue
            if filters.district_id and c.get("district_id") != filters.district_id:
                continue
            if filters.station_id and c.get("station_id") != filters.station_id:
                continue
            if filters.crime_category and c.get("crime_type") != filters.crime_category:
                continue
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                hourly[dt.hour] += 1
                daily[dt.strftime("%A")] += 1
                monthly[dt.strftime("%Y-%m")] += 1
                season = self._get_season(dt.month)
                seasonal[season] += 1
                total += 1
            except Exception as exception:
                logger.warning("Failed to parse created timestamp: %s\n%s", exception, traceback.format_exc())

        def pct(count: int) -> float:
            return round(count / max(total, 1) * 100, 2)

        hourly_dist = [TemporalDistribution(hour=h, count=count, percentage=pct(count)) for h, count in sorted(hourly.items())]
        daily_dist = [TemporalDistribution(day_of_week=d, count=count, percentage=pct(count)) for d, count in sorted(daily.items())]
        monthly_dist = [TemporalDistribution(month=m, count=count, percentage=pct(count)) for m, count in sorted(monthly.items())]
        seasonal_dist = [TemporalDistribution(season=s, count=count, percentage=pct(count)) for s, count in sorted(seasonal.items())]

        peak_hour = max(hourly, key=hourly.get) if hourly else None
        peak_day = max(daily, key=daily.get) if daily else None
        peak_month = max(monthly, key=monthly.get) if monthly else None
        peak_season = max(seasonal, key=seasonal.get) if seasonal else None

        return TemporalIntelligence(
            hourly_distribution=hourly_dist,
            daily_distribution=daily_dist,
            monthly_distribution=monthly_dist,
            seasonal_distribution=seasonal_dist,
            peak_hour=peak_hour,
            peak_day=peak_day,
            peak_month=peak_month,
            peak_season=peak_season,
        )

    async def get_trend_analysis(self, officer: Dict[str, Any], filters: Optional[PredictiveFilters] = None) -> TrendAnalysis:
        data = await self.repo.get_predictive_data(limit=2000)
        crimes = data.get("crimes", [])
        filters = filters or PredictiveFilters()

        now = datetime.now(timezone.utc)
        current_start = now - timedelta(days=30)
        previous_start = now - timedelta(days=60)

        current: Dict[str, int] = defaultdict(int)
        previous: Dict[str, int] = defaultdict(int)

        for c in crimes:
            created = c.get("CREATEDTIME", "")
            if not created:
                continue
            if filters.district_id and c.get("district_id") != filters.district_id:
                continue
            if filters.station_id and c.get("station_id") != filters.station_id:
                continue
            cat = c.get("crime_type", "Unknown")
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if dt >= current_start:
                    current[cat] += 1
                elif dt >= previous_start:
                    previous[cat] += 1
            except Exception as exception:
                logger.warning("Failed to parse created timestamp: %s\n%s", exception, traceback.format_exc())

        all_cats = set(current.keys()) | set(previous.keys())
        increasing: List[TrendCategory] = []
        decreasing: List[TrendCategory] = []
        stable: List[TrendCategory] = []

        for cat in sorted(all_cats):
            cc = current.get(cat, 0)
            pc = previous.get(cat, 0)
            if pc == 0:
                change = 100.0 if cc > 0 else 0.0
            else:
                change = round((cc - pc) / pc * 100, 2)
            tc = TrendCategory(category=cat, trend="stable", change_percent=change, count_current=cc, count_previous=pc)
            if change > 10:
                tc.trend = "increasing"
                increasing.append(tc)
            elif change < -10:
                tc.trend = "decreasing"
                decreasing.append(tc)
            else:
                stable.append(tc)

        emerging: List[EmergingPattern] = []
        for cat in increasing[:5]:
            emerging.append(EmergingPattern(
                pattern_type="crime_spike",
                description=f"{cat.category} crimes increased by {cat.change_percent}% in the last 30 days.",
                affected_entities=[cat.category],
                confidence=min(0.9, 0.5 + abs(cat.change_percent) / 100),
                severity="High" if abs(cat.change_percent) > 50 else "Medium",
            ))

        total_current = sum(current.values())
        total_previous = sum(previous.values())
        overall = "increasing" if total_current > total_previous else "decreasing" if total_current < total_previous else "stable"

        return TrendAnalysis(
            increasing_categories=sorted(increasing, key=lambda x: x.change_percent, reverse=True)[:10],
            decreasing_categories=sorted(decreasing, key=lambda x: x.change_percent)[:10],
            stable_categories=stable[:10],
            emerging_patterns=emerging[:10],
            overall_trend=overall,
        )

    async def simulate_scenario(self, officer: Dict[str, Any], scenario: ScenarioFilters) -> ScenarioSimulation:
        filters = PredictiveFilters(
            district_id=scenario.district_id,
            station_id=scenario.station_id,
            crime_category=scenario.crime_category,
            time_period=scenario.time_window or "30d",
        )
        forecast = await self.get_forecast(officer, filters)
        risk = await self.get_dynamic_risk_index(officer, filters)
        hotspots = await self.get_emerging_hotspots(officer, filters)
        patrols = await self.get_patrol_recommendations(officer, filters)

        forecast_dict = {
            "total_predicted": sum(f.total_predicted for f in forecast),
            "periods": [f.period for f in forecast],
            "entities": len(forecast),
        }
        risk_dict = {
            "highest_risk": risk[0].risk_score if risk else 0,
            "average_risk": round(sum(r.risk_score for r in risk) / max(len(risk), 1), 2),
            "entities": len(risk),
        }
        hotspots_list = [h.model_dump(mode="json") for h in hotspots[:10]]
        patrols_list = [p.model_dump(mode="json") for p in patrols[:10]]

        return ScenarioSimulation(
            filters=scenario,
            forecast=forecast_dict,
            risk=risk_dict,
            hotspots=hotspots_list,
            patrol_recommendations=patrols_list,
        )

    async def get_predictive_dashboard(self, officer: Dict[str, Any], filters: Optional[PredictiveFilters] = None) -> PredictiveDashboard:
        risk = await self.get_dynamic_risk_index(officer, filters)
        trends = await self.get_trend_analysis(officer, filters)
        hotspots = await self.get_emerging_hotspots(officer, filters)
        forecast = await self.get_forecast(officer, filters)

        highest_risk = risk[0] if risk else None
        fastest_growing = trends.increasing_categories[0] if trends.increasing_categories else None
        emerging = hotspots[0] if hotspots else None
        avg_confidence = round(sum(f.confidence for f in forecast) / max(len(forecast), 1), 2)
        patrol_increase = sum(1 for r in risk if r.risk_score >= 25)

        return PredictiveDashboard(
            highest_risk_district=highest_risk.model_dump(mode="json") if highest_risk else {},
            fastest_growing_crime=fastest_growing.model_dump(mode="json") if fastest_growing else {},
            emerging_hotspot=emerging.model_dump(mode="json") if emerging else {},
            forecast_confidence=avg_confidence,
            recommended_patrol_increase=patrol_increase,
            predicted_incident_count=sum(f.total_predicted for f in forecast),
            time_period=filters.time_period or "next_30_days",
        )

    async def get_ai_intelligence(self, officer: Dict[str, Any], filters: Optional[PredictiveFilters] = None) -> PredictiveAIExplanation:
        dashboard = await self.get_predictive_dashboard(officer, filters)
        trends = await self.get_trend_analysis(officer, filters)
        risk = await self.get_dynamic_risk_index(officer, filters)

        try:
            service = ExecutiveIntelligenceService(self.request)
            _ = service  # available for future direct integration
        except Exception as exception:
            logger.warning("AI intelligence integration failed: %s\n%s", exception, traceback.format_exc())

        forecast_text = f"Forecast for the next period predicts {dashboard.predicted_incident_count} incidents with {round(dashboard.forecast_confidence * 100)}% confidence."
        risk_text = f"Highest risk district is {dashboard.highest_risk_district.get('entity_name', 'N/A')} with score {dashboard.highest_risk_district.get('risk_score', 0)}."
        strategies = [
            f"Increase patrol allocation by {dashboard.recommended_patrol_increase} units in high-risk zones.",
            f"Focus surveillance on {', '.join(c.category for c in trends.increasing_categories[:3])} crime categories.",
        ]
        if dashboard.emerging_hotspot:
            strategies.append(f"Deploy rapid response to {dashboard.emerging_hotspot.get('district_name', 'identified hotspot')}.")

        summary = (
            f"Executive Predictive Summary: {dashboard.predicted_incident_count} incidents forecasted. "
            f"Fastest growing crime: {dashboard.fastest_growing_crime.get('category', 'N/A')} "
            f"({dashboard.fastest_growing_crime.get('change_percent', 0)}% increase). "
            f"Confidence level: {round(dashboard.forecast_confidence * 100)}%."
        )

        return PredictiveAIExplanation(
            forecast_explanation=forecast_text,
            risk_explanation=risk_text,
            strategy_recommendations=strategies,
            executive_summary=summary,
            confidence=dashboard.forecast_confidence,
            is_fallback=True,
        )

    def _get_season(self, month: int) -> str:
        if month in (12, 1, 2):
            return "Winter"
        if month in (3, 4, 5):
            return "Summer"
        if month in (6, 7, 8):
            return "Monsoon"
        return "Post-Monsoon"
