"""
Prompt Builder

Builds strict system/user prompts for Catalyst AI across all
SurakshaIQ intelligence capabilities.
"""

from typing import Any, Dict, List, Optional


SYSTEM_PROMPT = (
    "You are a Senior Crime Intelligence Analyst for the Karnataka State Crime Records Bureau. "
    "You produce concise, structured executive intelligence briefings for senior police officers. "
    "Use ONLY the supplied analytics. Do not hallucinate. "
    "Write in a professional, operational tone. Avoid conversational language."
)

CHAT_SYSTEM_PROMPT = (
    "You are an operational police intelligence assistant for the Karnataka State Police. "
    "Answer questions using ONLY the supplied analytics context. "
    "If the answer is not in the context, say 'I cannot answer from the current analytics.' "
    "Be concise, factual, and actionable. Include specific numbers and locations when available."
)

FIR_SYSTEM_PROMPT = (
    "You are a criminal intelligence analyst for the Karnataka State Police. "
    "Analyze the supplied FIR data and extract actionable intelligence. "
    "Return strict JSON only."
)

PATTERN_SYSTEM_PROMPT = (
    "You are a crime pattern analyst for the Karnataka State Crime Records Bureau. "
    "Detect hidden correlations and explainable patterns across time, location, offender, and crime category. "
    "Return strict JSON only."
)

RECOMMENDATION_SYSTEM_PROMPT = (
    "You are an operational policing strategist for the Karnataka State Police. "
    "Generate actionable deployment and investigation recommendations. "
    "Prioritize by impact and feasibility. Return strict JSON only."
)

REPORT_SYSTEM_PROMPT = (
    "You are an intelligence report writer for the Karnataka State Police. "
    "Generate a structured intelligence report from dashboard analytics. "
    "Use professional police terminology. Return strict JSON only."
)

EXPLAIN_SYSTEM_PROMPT = (
    "You are a policing analytics explainability expert. "
    "Explain why a pattern exists in the supplied chart/map data and what action should be taken. "
    "Be concise and actionable. Return strict JSON only."
)

EVIDENCE_SYSTEM_PROMPT = (
    "You are a criminal investigator for the Karnataka State Police. "
    "Summarize the supplied evidence document into structured intelligence. "
    "Extract entities, key facts, and investigative value. Return strict JSON only."
)

TIMELINE_SYSTEM_PROMPT = (
    "You are a forensic timeline analyst for the Karnataka State Police. "
    "Convert the supplied incident description into a chronological investigative timeline. "
    "Identify key events, actors, and evidence points. Return strict JSON only."
)


def build_executive_prompt(analytics: Dict[str, Any]) -> List[Dict[str, str]]:
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

    user_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        "Generate an executive intelligence briefing from the following analytics.\n\n"
        "Intelligence Scope:\n{intelligence_scope}\n\n"
        "KPI Metrics:\n{kpi_metrics}\n\n"
        "Crime Trends:\n{crime_trends}\n\n"
        "Hotspots:\n{hotspots}\n\n"
        "District Statistics:\n{district_statistics}\n\n"
        "Crime Category Distribution:\n{crime_category_distribution}\n\n"
        "Network Analysis Summary:\n{network_summary}\n\n"
        "Repeat Offender Statistics:\n{repeat_offender_summary}\n\n"
        "Alerts:\n{alerts}\n\n"
        "Risk Scores:\n{risk_scores}\n\n"
        "Recent Incidents:\n{recent_incidents}\n\n"
        "Required output (strict JSON only, no markdown):\n"
        '{{\n'
        '  "overallRisk": "High | Medium | Low",\n'
        '  "executiveSummary": "...",\n'
        '  "keyFindings": ["...", "..."],\n'
        '  "recommendedActions": ["...", "..."],\n'
        '  "confidence": 0.0-1.0\n'
        '}}'
    ).format(**formatted_fields)

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def build_chat_prompt(question: str, analytics: Dict[str, Any]) -> List[Dict[str, str]]:
    formatted = {
        "kpi_metrics": _format_block(analytics.get("kpi_metrics", {})),
        "hotspots": _format_list(analytics.get("hotspots", []), "hotspot"),
        "alerts": _format_list(analytics.get("alerts", []), "alert"),
        "crime_trends": _format_list(analytics.get("crime_trends", []), "crime_trend"),
        "district_stats": _format_list(analytics.get("district_statistics", []), "district"),
        "anomalies": _format_list(analytics.get("anomalies", []), "anomaly"),
        "repeat_offenders": _format_list(analytics.get("repeat_offender_statistics", {}).get("top_offenders", []), "repeat_offender"),
        "network_summary": _format_block(analytics.get("network_analysis_summary", {})),
    }

    user_prompt = (
        f"{CHAT_SYSTEM_PROMPT}\n\n"
        f"User Question: {question}\n\n"
        "Current Analytics Context:\n"
        "KPI Metrics:\n{kpi_metrics}\n\n"
        "Hotspots:\n{hotspots}\n\n"
        "Alerts:\n{alerts}\n\n"
        "Crime Trends:\n{crime_trends}\n\n"
        "District Statistics:\n{district_stats}\n\n"
        "Anomalies:\n{anomalies}\n\n"
        "Repeat Offenders:\n{repeat_offenders}\n\n"
        "Network Summary:\n{network_summary}\n\n"
        "Answer the user question using ONLY the above analytics. "
        "If the answer cannot be determined from the analytics, say so explicitly."
    ).format(**formatted)

    return [
        {"role": "system", "content": CHAT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def build_fir_intelligence_prompt(fir_payload: Dict[str, Any]) -> List[Dict[str, str]]:
    fields = {
        "fir_number": fir_payload.get("fir_number", "N/A"),
        "description": fir_payload.get("description", "N/A"),
        "sections": fir_payload.get("sections", "N/A"),
        "victim_name": fir_payload.get("victim_name", "N/A"),
        "suspect_name": fir_payload.get("suspect_name", "N/A"),
        "district_id": fir_payload.get("district_id", "N/A"),
        "station_id": fir_payload.get("station_id", "N/A"),
        "status": fir_payload.get("status", "N/A"),
    }

    user_prompt = (
        f"{FIR_SYSTEM_PROMPT}\n\n"
        "Analyze the following FIR record and return strictly:\n"
        '{{\n'
        '  "crime_category": "...",\n'
        '  "severity": "Critical | High | Medium | Low",\n'
        '  "modus_operandi": "...",\n'
        '  "entities": {{"people": [...], "locations": [...], "vehicles": [...], "phones": [...]}},\n'
        '  "investigation_suggestions": ["...", "..."],\n'
        '  "confidence": 0.0-1.0\n'
        '}}\n\n'
        "FIR Data:\n"
        f"  FIR Number: {fields['fir_number']}\n"
        f"  Description: {fields['description']}\n"
        f"  Sections: {fields['sections']}\n"
        f"  Victim: {fields['victim_name']}\n"
        f"  Suspect: {fields['suspect_name']}\n"
        f"  District: {fields['district_id']}\n"
        f"  Station: {fields['station_id']}\n"
        f"  Status: {fields['status']}\n"
    )

    return [
        {"role": "system", "content": FIR_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def build_pattern_discovery_prompt(analytics: Dict[str, Any]) -> List[Dict[str, str]]:
    formatted = {
        "hotspots": _format_list(analytics.get("hotspots", []), "hotspot"),
        "crime_trends": _format_list(analytics.get("crime_trends", []), "trend"),
        "district_stats": _format_list(analytics.get("district_statistics", []), "district"),
        "alerts": _format_list(analytics.get("alerts", []), "alert"),
        "repeat_offenders": _format_block(analytics.get("repeat_offender_statistics", {})),
        "risk_scores": _format_list(analytics.get("risk_scores", []), "risk_score"),
        "network_summary": _format_block(analytics.get("network_analysis_summary", {})),
    }

    user_prompt = (
        f"{PATTERN_SYSTEM_PROMPT}\n\n"
        "Analyze the following dashboard analytics for hidden correlations.\n\n"
        "Return strictly JSON with this schema:\n"
        '{{\n'
        '  "patterns": [{{"type": "...", "description": "...", "entities_involved": [...]}}],\n'
        '  "correlations": [{{"type": "...", "description": "...", "entities_involved": [...]}}],\n'
        '  "confidence": 0.0-1.0\n'
        '}}\n\n'
        "Hotspots:\n{hotspots}\n\n"
        "Crime Trends:\n{crime_trends}\n\n"
        "District Statistics:\n{district_stats}\n\n"
        "Alerts:\n{alerts}\n\n"
        "Repeat Offender Statistics:\n{repeat_offenders}\n\n"
        "Risk Scores:\n{risk_scores}\n\n"
        "Network Summary:\n{network_summary}\n"
    ).format(**formatted)

    return [
        {"role": "system", "content": PATTERN_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def build_recommendation_prompt(analytics: Dict[str, Any]) -> List[Dict[str, str]]:
    formatted = {
        "kpi_metrics": _format_block(analytics.get("kpi_metrics", {})),
        "hotspots": _format_list(analytics.get("hotspots", []), "hotspot"),
        "alerts": _format_list(analytics.get("alerts", []), "alert"),
        "district_stats": _format_list(analytics.get("district_statistics", []), "district"),
        "risk_scores": _format_list(analytics.get("risk_scores", []), "risk_score"),
        "repeat_offenders": _format_block(analytics.get("repeat_offender_statistics", {})),
    }

    user_prompt = (
        f"{RECOMMENDATION_SYSTEM_PROMPT}\n\n"
        "Generate operational recommendations based on the following analytics.\n\n"
        "Return strictly JSON with this schema:\n"
        '{{\n'
        '  "recommendations": [\n'
        '    {{"title": "...", "description": "...", "priority": "high | medium | low", "category": "patrol_deployment | investigation_priority | surveillance | checkpoints | resource_allocation"}}\n'
        '  ],\n'
        '  "overall_risk": "High | Medium | Low",\n'
        '  "confidence": 0.0-1.0\n'
        '}}\n\n'
        "KPI Metrics:\n{kpi_metrics}\n\n"
        "Hotspots:\n{hotspots}\n\n"
        "Alerts:\n{alerts}\n\n"
        "District Statistics:\n{district_stats}\n\n"
        "Risk Scores:\n{risk_scores}\n\n"
        "Repeat Offender Statistics:\n{repeat_offenders}\n"
    ).format(**formatted)

    return [
        {"role": "system", "content": RECOMMENDATION_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def build_report_prompt(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    analytics = payload.get("analytics", {})
    report_type = payload.get("report_type", "SUMMARY")
    scope = payload.get("scope", {})

    formatted = {
        "report_type": report_type,
        "scope": _format_block(scope),
        "kpi_metrics": _format_block(analytics.get("kpi_metrics", {})),
        "hotspots": _format_list(analytics.get("hotspots", []), "hotspot"),
        "alerts": _format_list(analytics.get("alerts", []), "alert"),
        "crime_trends": _format_list(analytics.get("crime_trends", []), "trend"),
        "district_stats": _format_list(analytics.get("district_statistics", []), "district"),
        "risk_scores": _format_list(analytics.get("risk_scores", []), "risk_score"),
        "repeat_offenders": _format_block(analytics.get("repeat_offender_statistics", {})),
        "network_summary": _format_block(analytics.get("network_analysis_summary", {})),
    }

    user_prompt = (
        f"{REPORT_SYSTEM_PROMPT}\n\n"
        "Generate a structured intelligence report.\n\n"
        f"Report Type: {report_type}\n"
        f"Scope: {formatted['scope']}\n\n"
        "Return strictly JSON with this schema:\n"
        '{{\n'
        '  "reportId": "auto-generated",\n'
        '  "title": "...",\n'
        '  "content": "...",\n'
        '  "format": "text",\n'
        '  "sections": [{{"title": "...", "content": "..."}}],\n'
        '  "confidence": 0.0-1.0\n'
        '}}\n\n'
        "Analytics:\n"
        "KPI Metrics:\n{kpi_metrics}\n\n"
        "Hotspots:\n{hotspots}\n\n"
        "Alerts:\n{alerts}\n\n"
        "Crime Trends:\n{crime_trends}\n\n"
        "District Statistics:\n{district_stats}\n\n"
        "Risk Scores:\n{risk_scores}\n\n"
        "Repeat Offender Statistics:\n{repeat_offenders}\n\n"
        "Network Summary:\n{network_summary}\n"
    ).format(**formatted)

    return [
        {"role": "system", "content": REPORT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def build_explain_prompt(chart_type: str, data: Dict[str, Any], filters: Dict[str, Any]) -> List[Dict[str, str]]:
    formatted = {
        "chart_type": chart_type,
        "filters": _format_block(filters),
        "data": _format_block(data),
    }

    user_prompt = (
        f"{EXPLAIN_SYSTEM_PROMPT}\n\n"
        "Explain the pattern in the following chart/map data and recommend actions.\n\n"
        "Return strictly JSON with this schema:\n"
        '{{\n'
        '  "explanation": "...",\n'
        '  "confidence": 0.0-1.0\n'
        '}}\n\n'
        "Chart Type: {chart_type}\n\n"
        "Filters Applied:\n{filters}\n\n"
        "Data:\n{data}\n"
    ).format(**formatted)

    return [
        {"role": "system", "content": EXPLAIN_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def build_evidence_summary_prompt(document_type: str, content: str) -> List[Dict[str, str]]:
    user_prompt = (
        f"{EVIDENCE_SYSTEM_PROMPT}\n\n"
        "Summarize the following evidence document.\n\n"
        "Return strictly JSON with this schema:\n"
        '{{\n'
        '  "summary": "...",\n'
        '  "extracted_entities": {{"people": [...], "locations": [...], "vehicles": [...], "phones": [...]}},\n'
        '  "key_points": ["...", "..."],\n'
        '  "confidence": 0.0-1.0\n'
        '}}\n\n'
        f"Document Type: {document_type}\n\n"
        f"Content:\n{content[:4000]}\n"
    )

    return [
        {"role": "system", "content": EVIDENCE_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def build_timeline_prompt(incident_description: str) -> List[Dict[str, str]]:
    user_prompt = (
        f"{TIMELINE_SYSTEM_PROMPT}\n\n"
        "Convert the following incident description into a chronological investigative timeline.\n\n"
        "Return strictly JSON with this schema:\n"
        '{{\n'
        '  "events": [{{"timestamp": "...", "event": "...", "evidence": "...", "actor": "..."}}],\n'
        '  "narrative": "...",\n'
        '  "confidence": 0.0-1.0\n'
        '}}\n\n'
        f"Incident Description:\n{incident_description[:4000]}\n"
    )

    return [
        {"role": "system", "content": TIMELINE_SYSTEM_PROMPT},
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
