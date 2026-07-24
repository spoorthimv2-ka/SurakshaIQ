"""
Local Fallback Intelligence Generator

Generates a deterministic executive briefing when Catalyst AI is unavailable.
"""

from typing import Any, Dict, List

from app.services.ai.analytics_aggregator import aggregate_dashboard_analytics


def generate_local_briefing(analytics: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a structured executive briefing from dashboard analytics."""
    total_crimes = analytics.get("kpi_metrics", {}).get("total_crimes", 0)
    active_firs = analytics.get("kpi_metrics", {}).get("active_firs", 0)
    closed_firs = analytics.get("kpi_metrics", {}).get("closed_firs", 0)
    detection_rate = analytics.get("kpi_metrics", {}).get("detection_rate", 0.0)

    hotspots = analytics.get("hotspots", []) or []
    alerts = analytics.get("alerts", []) or []
    trends = analytics.get("crime_trends", []) or []
    districts = analytics.get("district_statistics", []) or []

    critical_hotspots = [h for h in hotspots if str(h.get("riskLevel", "")).lower() in {"critical", "high"}]
    risk = "High" if (len(critical_hotspots) > 0 or detection_rate < 45) else "Medium"
    if total_crimes == 0 and active_firs == 0:
        risk = "Low"

    key_findings: List[str] = []
    if trends:
        first = trends[0].get("count", 0)
        last = trends[-1].get("count", 0)
        if first > 0:
            change = ((last - first) / first) * 100
            key_findings.append(
                f"Crime volume {'increased' if change > 0 else 'decreased'} {abs(change):.1f}% across the selected period."
            )
        else:
            key_findings.append("Crime volume trend is stable with limited historical variance.")

    key_findings.append(f"{len(critical_hotspots)} high-risk hotspot(s) require attention.")
    key_findings.append(f"Active caseload is {active_firs} with {closed_firs} closed.")

    recommended_actions = [
        "Increase patrol frequency in identified hotspots.",
        "Deploy additional mobile forensic units for active investigations.",
        "Monitor repeat offenders in high-frequency jurisdictions.",
        "Enhance surveillance coverage using available CCTV infrastructure.",
    ]
    if active_firs > 50:
        recommended_actions.append("Consider mobilizing additional investigative staff to reduce backlog.")

    summary = (
        f"Karnataka crime situation is {risk.lower()} risk. "
        f"{active_firs} active FIRs and {closed_firs} resolved. "
        f"{len(critical_hotspots)} high-risk locations flagged."
    )

    return {
        "overallRisk": risk,
        "executiveSummary": summary,
        "keyFindings": key_findings[:5],
        "recommendedActions": recommended_actions[:5],
        "confidence": 0.75,
        "generatedAt": _now_iso(),
        "isFallback": True,
    }


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
