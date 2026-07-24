"""
Prompt Builder

Builds a strict system/user prompt for Catalyst AI to produce
executive intelligence briefings from normalized analytics payloads.
"""

from typing import Any, Dict, List

SYSTEM_PROMPT = (
    "You are a Senior Crime Intelligence Analyst for the Karnataka State Crime Records Bureau. "
    "You produce concise, structured executive intelligence briefings for senior police officers. "
    "Use ONLY the supplied analytics. Do not hallucinate. "
    "Write in a professional, operational tone. Avoid conversational language."
)

USER_PROMPT_TEMPLATE = """
Intelligence Scope:
{intelligence_scope}

KPI Metrics:
{kpi_metrics}

Crime Trends:
{crime_trends}

Hotspots:
{hotspots}

District Statistics:
{district_statistics}

Crime Category Distribution:
{crime_category_distribution}

Network Analysis Summary:
{network_summary}

Repeat Offender Statistics:
{repeat_offender_summary}

Alerts:
{alerts}

Risk Scores:
{risk_scores}

Recent Incidents:
{recent_incidents}

Required output (strict JSON only, no markdown):
{{
  "overallRisk": "High | Medium | Low",
  "executiveSummary": "...",
  "keyFindings": ["...", "..."],
  "recommendedActions": ["...", "..."],
  "confidence": 0.0-1.0
}}
"""


def build_executive_prompt(analytics: Dict[str, Any]) -> List[Dict[str, str]]:
    """Return chat messages for Catalyst AI."""
    formatted_fields = {
        "intelligence_scope": _format_block(analytics.get("intelligence_scope", {})),
        "kpi_metrics": _format_block(analytics.get("kpi_metrics", {})),
        "crime_trends": _format_list(analytics.get("crime_trends", []), "crime_trends"),
        "hotspots": _format_list(analytics.get("hotspots", []), "hotspot"),
        "district_statistics": _format_list(analytics.get("district_statistics", []), "district_statistic"),
        "crime_category_distribution": _format_list(analytics.get("crime_category_distribution", []), "category"),
        "network_summary": _format_block(analytics.get("network_analysis_summary", {})),
        "repeat_offender_summary": _format_block(analytics.get("repeat_offender_statistics", {})),
        "alerts": _format_list(analytics.get("alerts", []), "alert"),
        "risk_scores": _format_list(analytics.get("risk_scores", []), "risk_score"),
        "recent_incidents": _format_list(analytics.get("recent_incidents", []), "incident"),
    }

    user_prompt = USER_PROMPT_TEMPLATE.format(**formatted_fields)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def _format_block(value: Any) -> str:
    if isinstance(value, dict):
        lines = [f"{k}: {v}" for k, v in value.items()]
        return "\n".join(lines) if lines else "None"
    return str(value)


def _format_list(value: Any, label: str) -> str:
    if not value:
        return f"No {label} available."
    lines = []
    for idx, item in enumerate(value, 1):
        lines.append(f"{idx}. {_format_block(item)}")
    return "\n".join(lines)
