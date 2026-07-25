"""
Executive Intelligence Service

Orchestrates:
- Analytics aggregation
- Prompt construction
- Catalyst AI completion
- Fallback local intelligence generation
- Caching/policy decisions
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from app.config.settings import settings
from app.core.catalyst import catalyst_manager
from app.core.exceptions import RepositoryError
from app.core.logger import logger
from app.repositories.base_repository import BaseCatalystRepository
from app.services.ai.analytics_aggregator import aggregate_dashboard_analytics
from app.services.ai.catalyst_ai_client import CatalystAIClient
from app.services.ai.fallback_executive_intelligence import (
    generate_local_briefing,
    generate_local_chat_response,
    generate_local_fir_intelligence,
    generate_local_recommendations,
    generate_local_intelligence_report,
    generate_local_explanation,
    generate_local_evidence_summary,
    generate_local_timeline,
    generate_local_patterns,
)
from app.services.ai.prompt_builder import (
    build_executive_prompt,
    build_chat_prompt,
    build_fir_intelligence_prompt,
    build_pattern_discovery_prompt,
    build_recommendation_prompt,
    build_report_prompt,
    build_explain_prompt,
    build_evidence_summary_prompt,
    build_timeline_prompt,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ExecutiveIntelligenceService(BaseCatalystRepository):
    """AI-enabled operational intelligence service."""

    def __init__(self, request: Any):
        super().__init__(request, table_name="Search")

    @staticmethod
    def _is_ai_available() -> bool:
        return CatalystAIClient.is_configured() and settings.ai_fallback_enabled is not False

    async def generate_executive_summary(
        self,
        *,
        filters: Optional[Dict[str, Any]] = None,
        intelligence_scope: Optional[Dict[str, Any]] = None,
        dashboard_payload: Optional[Dict[str, Any]] = None,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """Generate or retrieve a cached operational police briefing."""
        slug = self._build_slug(filters, intelligence_scope)

        if not force_refresh:
            cached = self._read_cache(slug)
            if cached:
                logger.info(f"Returning cached executive summary: {slug}")
                return cached

        analytics = aggregate_dashboard_analytics(
            intelligence_scope=intelligence_scope,
            kpi_metrics=(dashboard_payload or {}).get("kpi_metrics"),
            crime_trends=(dashboard_payload or {}).get("crime_trends"),
            hotspots=(dashboard_payload or {}).get("hotspots"),
            district_stats=(dashboard_payload or {}).get("district_stats"),
            crime_category_distribution=(dashboard_payload or {}).get("crime_category_distribution"),
            network_summary=(dashboard_payload or {}).get("network_summary"),
            repeat_offender_stats=(dashboard_payload or {}).get("repeat_offender_stats"),
            alerts=(dashboard_payload or {}).get("alerts"),
            risk_scores=(dashboard_payload or {}).get("risk_scores"),
            recent_incidents=(dashboard_payload or {}).get("recent_incidents"),
        )

        ai_used = False
        confidence = 0.75

        if not CatalystAIClient.is_configured():
            logger.warning("Catalyst AI unavailable. Using local fallback.")
            result = generate_local_briefing(analytics)
            self._write_cache(slug, result)
            return result

        try:
            ai_client = CatalystAIClient(self.request)
            messages = build_executive_prompt(analytics)
            completion = await ai_client.generate_completion(
                messages=messages,
                response_format={"type": "json_object"},
            )
            parsed = _parse_completion(completion.get("content", "{}"))
            parsed["generatedAt"] = _now_iso()
            parsed["isFallback"] = False
            parsed["analyticsUsed"] = _derive_analytics_used(parsed)
            if "confidence" in parsed:
                try:
                    confidence = float(parsed["confidence"])
                    confidence = max(0.0, min(1.0, confidence))
                except (TypeError, ValueError):
                    pass
            parsed["confidence"] = confidence
            parsed["model"] = completion.get("model")
            self._write_cache(slug, parsed)
            return parsed
        except RepositoryError as e:
            logger.error(f"AI generation failed: {e}. Falling back to local briefing.")
            result = generate_local_briefing(analytics)
            self._write_cache(slug, result)
            return result

    async def analyze_fir(self, fir_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an FIR record and extract structured intelligence."""
        messages = build_fir_intelligence_prompt(fir_payload)
        ai_client = CatalystAIClient(self.request)
        completion = await ai_client.generate_completion(
            messages=messages,
            temperature=settings.ai_temperature,
            max_tokens=settings.ai_max_tokens,
            response_format={"type": "json_object"},
        )
        parsed = _parse_completion(completion.get("content", "{}"))
        parsed["generatedAt"] = _now_iso()
        parsed["isFallback"] = False
        parsed["analyticsUsed"] = ["fir_payload"]
        parsed["model"] = completion.get("model")
        return parsed

    async def generate_recommendations(self, dashboard_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate operational recommendations from dashboard analytics."""
        analytics = aggregate_dashboard_analytics(
            kpi_metrics=dashboard_payload.get("kpi_metrics"),
            crime_trends=dashboard_payload.get("crime_trends"),
            hotspots=dashboard_payload.get("hotspots"),
            district_stats=dashboard_payload.get("district_stats"),
            network_summary=dashboard_payload.get("network_summary"),
            repeat_offender_stats=dashboard_payload.get("repeat_offender_stats"),
            alerts=dashboard_payload.get("alerts"),
            risk_scores=dashboard_payload.get("risk_scores"),
            recent_incidents=dashboard_payload.get("recent_incidents"),
        )

        if not CatalystAIClient.is_configured():
            result = generate_local_recommendations(analytics)
            return result.get("recommendations", [])

        messages = build_recommendation_prompt(analytics)
        ai_client = CatalystAIClient(self.request)
        completion = await ai_client.generate_completion(
            messages=messages,
            temperature=settings.ai_temperature,
            max_tokens=settings.ai_max_tokens,
            response_format={"type": "json_object"},
        )
        parsed = _parse_completion(completion.get("content", "{}"))
        if "confidence" not in parsed:
            parsed["confidence"] = 0.75
        parsed["generatedAt"] = _now_iso()
        parsed["isFallback"] = False
        parsed["analyticsUsed"] = _derive_analytics_used_recommendations(parsed)
        parsed["model"] = completion.get("model")
        return parsed

    async def answer_question(self, question: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Answer a conversational question from dashboard analytics."""
        analytics = context.get("analytics", {}) if context else {}
        messages = build_chat_prompt(question, analytics)

        if not CatalystAIClient.is_configured():
            result = generate_local_chat_response(question, analytics)
            return result

        ai_client = CatalystAIClient(self.request)
        completion = await ai_client.generate_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=500,
        )
        result = {
            "response": completion.get("content", ""),
            "confidence": 0.8,
            "analyticsUsed": _derive_analytics_used(question, analytics),
            "isFallback": False,
            "model": completion.get("model"),
            "generatedAt": _now_iso(),
        }
        return result

    async def generate_intelligence_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a structured intelligence report."""
        if not CatalystAIClient.is_configured():
            result = generate_local_intelligence_report(payload)
            return result

        messages = build_report_prompt(payload)
        ai_client = CatalystAIClient(self.request)
        completion = await ai_client.generate_completion(
            messages=messages,
            temperature=settings.ai_temperature,
            max_tokens=settings.ai_max_tokens,
            response_format={"type": "json_object"},
        )
        parsed = _parse_completion(completion.get("content", "{}"))
        parsed.setdefault("reportId", f"RPT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
        parsed.setdefault("format", "text")
        parsed.setdefault("generatedAt", _now_iso())
        parsed["isFallback"] = False
        parsed["analyticsUsed"] = ["dashboard_analytics"]
        parsed["model"] = completion.get("model")
        if "confidence" not in parsed:
            parsed["confidence"] = 0.75
        return parsed

    async def predict_emerging_threats(self, dashboard_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Detect hidden crime patterns and correlations."""
        analytics = aggregate_dashboard_analytics(
            kpi_metrics=dashboard_payload.get("kpi_metrics"),
            crime_trends=dashboard_payload.get("crime_trends"),
            hotspots=dashboard_payload.get("hotspots"),
            district_stats=dashboard_payload.get("district_stats"),
            crime_category_distribution=dashboard_payload.get("crime_category_distribution"),
            network_summary=dashboard_payload.get("network_summary"),
            repeat_offender_stats=dashboard_payload.get("repeat_offender_stats"),
            alerts=dashboard_payload.get("alerts"),
            risk_scores=dashboard_payload.get("risk_scores"),
        )

        if not CatalystAIClient.is_configured():
            result = generate_local_patterns(analytics)
            return result

        messages = build_pattern_discovery_prompt(analytics)
        ai_client = CatalystAIClient(self.request)
        completion = await ai_client.generate_completion(
            messages=messages,
            temperature=settings.ai_temperature,
            max_tokens=settings.ai_max_tokens,
            response_format={"type": "json_object"},
        )
        parsed = _parse_completion(completion.get("content", "{}"))
        parsed.setdefault("generatedAt", _now_iso())
        parsed["isFallback"] = False
        parsed["analyticsUsed"] = [
            "hotspots",
            "crime_trends",
            "district_statistics",
            "alerts",
            "network_analysis_summary",
            "repeat_offender_statistics",
            "risk_scores",
        ]
        parsed["model"] = completion.get("model")
        if "confidence" not in parsed:
            parsed["confidence"] = 0.7
        return parsed

    async def _evidence_summary(self, document_type: str, content: str) -> Dict[str, Any]:
        """Summarize evidence documents."""
        messages = build_evidence_summary_prompt(document_type, content)
        ai_client = CatalystAIClient(self.request)
        completion = await ai_client.generate_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=800,
            response_format={"type": "json_object"},
        )
        parsed = _parse_completion(completion.get("content", "{}"))
        parsed.setdefault("generatedAt", _now_iso())
        parsed["isFallback"] = False
        parsed["analyticsUsed"] = [document_type]
        parsed["model"] = completion.get("model")
        if "confidence" not in parsed:
            parsed["confidence"] = 0.7
        return parsed

    async def _generate_timeline(self, incident_description: str) -> Dict[str, Any]:
        """Generate chronological investigative timeline."""
        messages = build_timeline_prompt(incident_description)
        ai_client = CatalystAIClient(self.request)
        completion = await ai_client.generate_completion(
            messages=messages,
            temperature=0.2,
            max_tokens=800,
            response_format={"type": "json_object"},
        )
        parsed = _parse_completion(completion.get("content", "{}"))
        parsed.setdefault("generatedAt", _now_iso())
        parsed["isFallback"] = False
        parsed["analyticsUsed"] = ["incident_description"]
        parsed["model"] = completion.get("model")
        if "confidence" not in parsed:
            parsed["confidence"] = 0.65
        return parsed

    # ------------------------------------------------------------------
    # Simple caching on the datastore-backed Search table.
    # ------------------------------------------------------------------
    def _build_slug(self, filters: Optional[Dict[str, Any]], intelligence_scope: Optional[Dict[str, Any]]) -> str:
        import json, hashlib
        payload = json.dumps({"filters": filters, "scope": intelligence_scope}, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:64]

    def _read_cache(self, slug: str) -> Optional[Dict[str, Any]]:
        try:
            rows = self.zcql.execute_query(
                f"SELECT * FROM Search WHERE ROWID = '{slug}' LIMIT 1"
            )
            for row in rows:
                data = row.get("Search", {})
                if data:
                    return data
        except Exception as e:
            logger.debug(f"AI cache read failed: {e}")
        return None

    def _write_cache(self, slug: str, result: Dict[str, Any]) -> None:
        try:
            payload = dict(result)
            payload["ROWID"] = slug
            payload["CREATEDTIME"] = _now_iso()
            keys = ", ".join(payload.keys())
            placeholders = ", ".join(["%s"] * len(payload))
            self.zcql.execute_query(
                f"INSERT INTO Search ({keys}) VALUES ({placeholders})",
                list(payload.values()),
            )
        except Exception as e:
            logger.debug(f"AI cache write failed: {e}")


def _parse_completion(content: str) -> Dict[str, Any]:
    import json, re
    try:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in completion")
        return json.loads(match.group(0))
    except Exception as e:
        logger.warning(f"Failed to parse AI JSON: {e}")
        return {
            "overallRisk": "Medium",
            "executiveSummary": content[:500],
            "keyFindings": ["AI response parsing failed."],
            "recommendedActions": ["Review dashboard data manually."],
            "confidence": 0.5,
            "isFallback": True,
            "generatedAt": _now_iso(),
        }


def _derive_analytics_used(parsed: Dict[str, Any]) -> List[str]:
    return parsed.get("analyticsUsed", ["dashboard_analytics"])


def _derive_analytics_used_recommendations(parsed: Dict[str, Any]) -> List[str]:
    return parsed.get("analyticsUsed", ["dashboard_analytics"])
