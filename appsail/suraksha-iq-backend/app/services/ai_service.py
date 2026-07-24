"""
Executive Intelligence Service

Orchestrates:
- Analytics aggregation
- Prompt construction
- Catalyst AI completion
- Fallback local briefing generation
- Caching/policy decisions
"""

from typing import Any, Dict, List, Optional

from app.config.settings import settings
from app.core.catalyst import catalyst_manager
from app.core.exceptions import RepositoryError
from app.core.logger import logger
from app.repositories.base_repository import BaseCatalystRepository
from app.services.ai.analytics_aggregator import aggregate_dashboard_analytics
from app.services.ai.catalyst_ai_client import CatalystAIClient
from app.services.ai.fallback_executive_intelligence import generate_local_briefing
from app.services.ai.prompt_builder import build_executive_prompt


class ExecutiveIntelligenceService(BaseCatalystRepository):
    """AI-enabled executive intelligence service.

    Future AI methods (analyzeFIR, generateRecommendations, answerQuestion,
    generateIntelligenceReport, predictEmergingThreats) can be added here
    without architectural changes.
    """

    def __init__(self, request: Any):
        super().__init__(request, table_name="Search")

    async def generate_executive_summary(
        self,
        *,
        filters: Optional[Dict[str, Any]] = None,
        intelligence_scope: Optional[Dict[str, Any]] = None,
        dashboard_payload: Optional[Dict[str, Any]] = None,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """Generate or retrieve a cached executive intelligence briefing."""
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

        if not CatalystAIClient.is_configured() or not settings.ai_fallback_enabled:
            logger.warning("Catalyst AI unavailable. Using local fallback.")
            result = generate_local_briefing(analytics)
            self._write_cache(slug, result)
            return result

        try:
            ai_client = CatalystAIClient(self.request)
            messages = build_executive_prompt(analytics)
            completion = await ai_client.generate_completion(
                response_format={"type": "json_object"}
            )
            parsed = _parse_completion(completion.get("content", "{}"))
            parsed["generatedAt"] = _now_iso()
            parsed["isFallback"] = False
            self._write_cache(slug, parsed)
            return parsed
        except RepositoryError as e:
            logger.error(f"AI generation failed: {e}. Falling back to local briefing.")
            result = generate_local_briefing(analytics)
            return result

    async def analyze_fir(self, fir_payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("analyze_fir is planned for a future phase.")

    async def generate_recommendations(self, dashboard_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        raise NotImplementedError("generate_recommendations is planned for a future phase.")

    async def answer_question(self, question: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        raise NotImplementedError("answer_question is planned for a future phase.")

    async def generate_intelligence_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("generate_intelligence_report is planned for a future phase.")

    async def predict_emerging_threats(self, dashboard_payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("predict_emerging_threats is planned for a future phase.")

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


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
