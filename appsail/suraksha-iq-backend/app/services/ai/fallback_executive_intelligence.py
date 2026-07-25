"""
Local Fallback Intelligence Generator

Generates deterministic intelligence responses when Catalyst AI is unavailable.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from app.services.ai.analytics_aggregator import aggregate_dashboard_analytics


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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
        "analyticsUsed": ["kpi_metrics", "hotspots", "crime_trends", "alerts"],
        "model": None,
    }


def generate_local_chat_response(question: str, analytics: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a deterministic chat response from analytics."""
    lower = question.lower()
    hotspots = analytics.get("hotspots", []) or []
    trends = analytics.get("crime_trends", []) or []
    alerts = analytics.get("alerts", []) or []
    districts = analytics.get("district_statistics", []) or []
    total_crimes = analytics.get("kpi_metrics", {}).get("total_crimes", 0)
    active_firs = analytics.get("kpi_metrics", {}).get("active_firs", 0)

    if "hotspot" in lower:
        count = len(hotspots)
        return {
            "response": f"Current analytics show {count} hotspots. "
                        f"{len([h for h in hotspots if str(h.get('severity','')).lower() in ('critical','high')])} are high/critical risk. "
                        "Focus patrol resources on these locations during peak hours.",
            "confidence": 0.7,
            "analyticsUsed": ["hotspots"],
            "isFallback": True,
            "model": None,
        }
    if "trend" in lower:
        if trends:
            first = trends[0].get("count", 0)
            last = trends[-1].get("count", 0)
            change = ((last - first) / first) * 100 if first > 0 else 0
            direction = "increasing" if change > 0 else "decreasing" if change < 0 else "stable"
            return {
                "response": f"Crime trends are {direction} by {abs(change):.1f}% over the selected period. "
                            f"Latest period count: {last}.",
                "confidence": 0.75,
                "analyticsUsed": ["crime_trends"],
                "isFallback": True,
                "model": None,
            }
        return {
            "response": "No trend data available in the current analytics window.",
            "confidence": 0.5,
            "analyticsUsed": [],
            "isFallback": True,
            "model": None,
        }
    if "district" in lower:
        if districts:
            top = sorted(districts, key=lambda d: d.get("crime_count", 0), reverse=True)[0]
            return {
                "response": f"Highest priority district: {top.get('district_name', 'Unknown')} "
                            f"with {top.get('crime_count', 0)} crimes and {top.get('active_investigations', 0)} active investigations.",
                "confidence": 0.7,
                "analyticsUsed": ["district_statistics"],
                "isFallback": True,
                "model": None,
            }
        return {
            "response": "District analytics are currently unavailable.",
            "confidence": 0.5,
            "analyticsUsed": [],
            "isFallback": True,
            "model": None,
        }
    if "anomal" in lower:
        return {
            "response": f"{len(alerts)} active alerts flagged as anomalies. "
                        "Review alert descriptions for immediate action items.",
            "confidence": 0.65,
            "analyticsUsed": ["alerts"],
            "isFallback": True,
            "model": None,
        }
    return {
        "response": f"Current operational picture: {total_crimes} total crimes, {active_firs} active FIRs. "
                    "I can analyze hotspots, trends, districts, and anomalies from current data.",
        "confidence": 0.6,
        "analyticsUsed": ["kpi_metrics"],
        "isFallback": True,
        "model": None,
    }


def generate_local_fir_intelligence(fir_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract structured intelligence from FIR payload."""
    description = str(fir_payload.get("description", "") or "")
    title = str(fir_payload.get("title", "") or "")
    text = f"{title} {description}".lower()

    crime_categories = ["theft", "robbery", "assault", "burglary", "fraud", "cybercrime", "murder", "rape", "kidnapping", "narcotics"]
    category = next((c for c in crime_categories if c in text), "Other")

    if category in {"murder", "rape", "kidnapping"}:
        severity = "Critical"
    elif category in {"robbery", "burglary", "fraud"}:
        severity = "High"
    elif category in {"assault", "narcotics"}:
        severity = "Medium"
    else:
        severity = "Low"

    modus_operandi_keywords = {
        "snatching": "Snatching",
        "burglary": "Burglary",
        "fraud": "Fraud/Impersonation",
        "online scam": "Online scam",
        "cyber": "Cybercrime",
        "weapon": "Armed",
        "knife": "Armed",
        "gun": "Armed",
    }
    mo = next((v for k, v in modus_operandi_keywords.items() if k in text), "Unknown")

    entities: Dict[str, List[str]] = {"people": [], "locations": [], "vehicles": [], "phones": []}
    import re
    phones = re.findall(r'\b[6-9]\d{9}\b', description)
    vehicles = re.findall(r'\bKA\d{2}[A-Z]{2}\d{4}\b', description)
    entities["phones"] = list(set(phones))
    entities["vehicles"] = list(set(vehicles))

    suggestions = [
        f"Priority: {severity}. Immediate supervision recommended.",
        f"Category: {category}. Deploy specialized units if applicable.",
        "Verify CCTV coverage at incident location.",
        "Cross-reference with repeat offenders database.",
        "Secure forensic evidence within 48 hours.",
    ]

    return {
        "crime_category": category,
        "severity": severity,
        "modus_operandi": mo,
        "entities": entities,
        "investigation_suggestions": suggestions,
        "confidence": 0.7,
        "generatedAt": _now_iso(),
        "isFallback": True,
        "analyticsUsed": ["fir_payload"],
        "model": None,
    }


def generate_local_recommendations(analytics: Dict[str, Any]) -> Dict[str, Any]:
    """Generate deterministic operational recommendations."""
    hotspots = analytics.get("hotspots", []) or []
    alerts = analytics.get("alerts", []) or []
    districts = analytics.get("district_statistics", []) or []
    total_crimes = analytics.get("kpi_metrics", {}).get("total_crimes", 0)
    active_firs = analytics.get("kpi_metrics", {}).get("active_firs", 0)

    critical_hotspots = [h for h in hotspots if str(h.get("severity", "")).lower() in {"critical", "high"}]
    critical_alerts = [a for a in alerts if str(a.get("severity", "")).lower() in {"critical", "high"}]

    recommendations = []
    if critical_hotspots:
        recommendations.append({
            "title": "Deploy patrols to critical hotspots",
            "description": f"Immediate patrol deployment recommended for {len(critical_hotspots)} high-risk location(s).",
            "priority": "high",
            "category": "patrol_deployment",
        })
    if critical_alerts:
        recommendations.append({
            "title": "Address critical alerts",
            "description": f"{len(critical_alerts)} critical alerts require immediate operational response.",
            "priority": "high",
            "category": "investigation_priority",
        })
    if active_firs > 100:
        recommendations.append({
            "title": "Reduce FIR backlog",
            "description": f"{active_firs} active FIRs exceed operational capacity. Consider additional staff.",
            "priority": "medium",
            "category": "resource_allocation",
        })
    if districts:
        recommendations.append({
            "title": "Strengthen surveillance in high-crime districts",
            "description": "Deploy CCTV monitoring and static pickets in identified hotspots.",
            "priority": "medium",
            "category": "surveillance",
        })
    recommendations.append({
        "title": "Establish mobile checkpoints",
        "description": "Deploy vehicle checkpoints at strategic locations based on crime patterns.",
        "priority": "medium",
        "category": "checkpoints",
    })

    risk = "High" if (critical_hotspots or critical_alerts) else "Medium"
    return {
        "recommendations": recommendations,
        "overall_risk": risk,
        "confidence": 0.7,
        "generatedAt": _now_iso(),
        "isFallback": True,
        "analyticsUsed": ["hotspots", "alerts", "district_statistics", "kpi_metrics"],
        "model": None,
    }


def generate_local_intelligence_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a deterministic intelligence report."""
    report_type = payload.get("report_type", "SUMMARY")
    analytics = payload.get("analytics", {})
    total_crimes = analytics.get("kpi_metrics", {}).get("total_crimes", 0)
    active_firs = analytics.get("kpi_metrics", {}).get("active_firs", 0)
    hotspots = analytics.get("hotspots", []) or []

    report_id = f"RPT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    content = (
        f"INTELLIGENCE REPORT - {report_type}\n"
        f"Generated: {_now_iso()}\n\n"
        f"OVERVIEW\n"
        f"Total Crimes: {total_crimes}\n"
        f"Active FIRs: {active_firs}\n"
        f"Hotspots Flagged: {len(hotspots)}\n\n"
        f"KEY FINDINGS\n"
        f"- Crime patterns indicate moderate to high activity in flagged zones.\n"
        f"- Investigation backlog requires resource reallocation.\n"
        f"- Network analysis suggests repeat offender involvement in multiple cases.\n\n"
        f"RECOMMENDATIONS\n"
        f"- Increase patrol coverage in hotspot areas.\n"
        f"- Prioritize investigation of high-severity cases.\n"
        f"- Deploy surveillance assets strategically.\n"
    )

    sections = [
        {"title": "Executive Summary", "content": f"Operational overview: {total_crimes} crimes, {active_firs} active FIRs."},
        {"title": "Hotspot Analysis", "content": f"{len(hotspots)} locations flagged for priority attention."},
        {"title": "Recommendations", "content": "See body for detailed operational recommendations."},
    ]

    return {
        "reportId": report_id,
        "title": f"{report_type} Intelligence Report",
        "content": content,
        "format": "text",
        "sections": sections,
        "confidence": 0.7,
        "generatedAt": _now_iso(),
        "isFallback": True,
        "analyticsUsed": ["kpi_metrics", "hotspots"],
        "model": None,
    }


def generate_local_explanation(chart_type: str, data: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a deterministic explanation for a chart or map pattern."""
    chart_lower = str(chart_type).lower()
    if "hotspot" in chart_lower or "map" in chart_lower:
        hotspots = data.get("hotspots", []) or []
        critical = [h for h in hotspots if str(h.get("severity", "")).lower() in {"critical", "high"}]
        explanation = (
            f"Hotspot map shows {len(hotspots)} flagged locations, {len(critical)} of which are critical/high severity. "
            "Clusters typically indicate recurring criminal activity. "
            "Recommended action: deploy patrols and install temporary CCTV."
        )
    elif "trend" in chart_lower:
        trends = data.get("crime_trends", []) or []
        if len(trends) >= 2:
            first = trends[0].get("count", 0)
            last = trends[-1].get("count", 0)
            change = ((last - first) / first) * 100 if first > 0 else 0
            direction = "upward" if change > 0 else "downward" if change < 0 else "stable"
            explanation = (
                f"Trend chart shows a {direction} trajectory with {abs(change):.1f}% change. "
                "Upward trends suggest emerging crime waves requiring preventive patrols."
            )
        else:
            explanation = "Insufficient trend data to explain patterns."
    elif "anomaly" in chart_lower:
        anomalies = data.get("anomalies", []) or []
        explanation = (
            f"Anomaly detection flagged {len(anomalies)} patterns deviating from baseline. "
            "These may represent newly emerging crime patterns or data artifacts requiring validation."
        )
    else:
        explanation = "Pattern analysis unavailable for this chart type in offline mode."

    return {
        "explanation": explanation,
        "confidence": 0.65,
        "generatedAt": _now_iso(),
        "isFallback": True,
        "analyticsUsed": [chart_type],
        "model": None,
    }


def generate_local_evidence_summary(document_type: str, content: str) -> Dict[str, Any]:
    """Summarize an evidence document."""
    text = str(content or "")
    words = text.split()
    summary = text[:500] + "..." if len(text) > 500 else text

    import re
    phones = list(set(re.findall(r'\b[6-9]\d{9}\b', text)))
    vehicles = list(set(re.findall(r'\bKA\d{2}[A-Z]{2}\d{4}\b', text)))

    key_points = [
        "Document contains factual account of incident.",
        "Key entities extracted: phones, vehicles, locations.",
        "Cross-reference with FIR and charge sheet recommended.",
    ]

    return {
        "summary": summary or "No content provided.",
        "extracted_entities": {
            "people": [],
            "locations": [],
            "vehicles": vehicles,
            "phones": phones,
        },
        "key_points": key_points,
        "confidence": 0.65,
        "generatedAt": _now_iso(),
        "isFallback": True,
        "analyticsUsed": [document_type],
        "model": None,
    }


def generate_local_timeline(incident_description: str) -> Dict[str, Any]:
    """Generate a chronological timeline from incident description."""
    text = str(incident_description or "")
    events = [
        {
            "timestamp": "T-0",
            "event": "Incident reported / description recorded",
            "evidence": "Narrative document",
            "actor": "Complainant / Witness",
        }
    ]

    import re
    dates = re.findall(r'\d{4}-\d{2}-\d{2}', text)
    if dates:
        events[0]["timestamp"] = dates[0]
        events.append({
            "timestamp": dates[0],
            "event": "Incident date identified from description",
            "evidence": "Document metadata",
            "actor": "System",
        })

    narrative = (
        "Timeline reconstructed from incident description. "
        "Events are ordered chronologically based on extracted dates and narrative sequence. "
        "All timestamps should be verified against FIR registration time."
    )

    return {
        "events": events,
        "narrative": narrative,
        "confidence": 0.6,
        "generatedAt": _now_iso(),
        "isFallback": True,
        "analyticsUsed": ["incident_description"],
        "model": None,
    }


def generate_local_patterns(analytics: Dict[str, Any]) -> Dict[str, Any]:
    """Detect deterministic crime patterns."""
    hotspots = analytics.get("hotspots", []) or []
    districts = analytics.get("district_statistics", []) or []
    trends = analytics.get("crime_trends", []) or []
    alerts = analytics.get("alerts", []) or []

    patterns = []
    correlations = []

    if districts:
        top_district = sorted(districts, key=lambda d: d.get("crime_count", 0), reverse=True)[0]
        patterns.append({
            "type": "geographic_concentration",
            "description": f"{top_district.get('district_name', 'Unknown')} has the highest crime concentration.",
            "district_id": top_district.get("district_id"),
            "crime_count": top_district.get("crime_count", 0),
        })

    if trends and len(trends) >= 2:
        first = trends[0].get("count", 0)
        last = trends[-1].get("count", 0)
        if first > 0:
            change = ((last - first) / first) * 100
            if abs(change) > 10:
                patterns.append({
                    "type": "temporal_trend",
                    "description": f"Crime volume changed by {change:.1f}% over the analyzed period.",
                    "direction": "increasing" if change > 0 else "decreasing",
                    "magnitude": abs(change),
                })

    critical_hotspots = [h for h in hotspots if str(h.get("severity", "")).lower() in {"critical", "high"}]
    if critical_hotspots:
        patterns.append({
            "type": "hotspot_intensity",
            "description": f"{len(critical_hotspots)} locations show persistent high-severity activity.",
            "locations": [h.get("district", "") for h in critical_hotspots[:5]],
        })

    if alerts:
        correlations.append({
            "type": "alert_correlation",
            "description": f"{len(alerts)} active alerts may correlate with hotspot locations and repeat offenders.",
        })

    return {
        "patterns": patterns,
        "correlations": correlations,
        "confidence": 0.65 if patterns else 0.5,
        "generatedAt": _now_iso(),
        "isFallback": True,
        "analyticsUsed": ["hotspots", "district_statistics", "crime_trends", "alerts"],
        "model": None,
    }
