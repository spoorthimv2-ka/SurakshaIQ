"""
Analytics Aggregator

Collects dashboard intelligence into one structured payload for the AI prompt builder.
"""

from typing import Any, Dict, List, Optional


def aggregate_dashboard_analytics(
    *,
    intelligence_scope: Optional[Dict[str, Any]] = None,
    kpi_metrics: Optional[Dict[str, Any]] = None,
    crime_trends: Optional[List[Dict[str, Any]]] = None,
    hotspots: Optional[List[Dict[str, Any]]] = None,
    district_stats: Optional[List[Dict[str, Any]]] = None,
    crime_category_distribution: Optional[List[Dict[str, Any]]] = None,
    network_summary: Optional[Dict[str, Any]] = None,
    repeat_offender_stats: Optional[Dict[str, Any]] = None,
    alerts: Optional[List[Dict[str, Any]]] = None,
    risk_scores: Optional[List[Dict[str, Any]]] = None,
    recent_incidents: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Normalize dashboard intelligence into a single analytics payload."""

    payload: Dict[str, Any] = {
        "intelligence_scope": _safe(intelligence_scope),
        "kpi_metrics": _safe(kpi_metrics) or {},
        "crime_trends": _safe(crime_trends) or [],
        "hotspots": _safe(hotspots) or [],
        "district_statistics": _safe(district_stats) or [],
        "crime_category_distribution": _safe(crime_category_distribution) or [],
        "network_analysis_summary": _safe(network_summary) or {},
        "repeat_offender_statistics": _safe(repeat_offender_stats) or {},
        "alerts": _safe(alerts) or [],
        "risk_scores": _safe(risk_scores) or [],
        "recent_incidents": _safe(recent_incidents) or [],
    }

    # basic sanitization for prompt consumption
    payload["kpi_metrics"] = _numbers_only(payload["kpi_metrics"])
    return payload


def _safe(value: Any) -> Any:
    if value is None:
        return {}
    return value


def _numbers_only(obj: Dict[str, Any]) -> Dict[str, Any]:
    sanitized: Dict[str, Any] = {}
    for k, v in obj.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            sanitized[k] = v
    return sanitized
