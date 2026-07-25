from fastapi import APIRouter, Depends, HTTPException, Request, Body, status
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import time

from app.api.deps import get_current_officer, RequirePermission
from app.models.enums import Permission
from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    ExecutiveIntelligenceResponse,
    SummaryResponse,
    FIRIntelligenceResponse,
    PatternDiscoveryResponse,
    RecommendationResponse,
    IntelligenceReportResponse,
    ExplanationResponse,
    EvidenceSummaryResponse,
    TimelineResponse,
)
from app.services.ai_service import ExecutiveIntelligenceService
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
from app.config.settings import settings

router = APIRouter()


# ============================================================
# Executive Intelligence
# ============================================================

@router.post(
    "/summary",
    response_model=ExecutiveIntelligenceResponse,
    summary="Executive Intelligence Summary",
    description="Generate an operational police intelligence briefing from dashboard analytics.",
)
async def executive_summary(
    request: Request,
    payload: Dict[str, Any] = Body(...),
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_AI_INVESTIGATION])),
):
    try:
        service = ExecutiveIntelligenceService(request)
        result = await service.generate_executive_summary(
            filters=payload.get("filters"),
            intelligence_scope=payload.get("intelligence_scope"),
            dashboard_payload=payload.get("dashboard_payload"),
            force_refresh=payload.get("force_refresh", False),
        )
        return ExecutiveIntelligenceResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate executive summary: {str(e)}",
        )


# ============================================================
# AI Chat
# ============================================================

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Police AI Chat",
    description="Conversational assistant that answers questions using current dashboard analytics.",
)
async def ai_chat(
    request: Request,
    body: ChatRequest,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_AI_INVESTIGATION])),
):
    try:
        context = body.context or {}
        analytics = context.get("analytics", {})

        if not ExecutiveIntelligenceService._is_ai_available():
            result = generate_local_chat_response(body.message, analytics)
            return ChatResponse(**result)

        service = ExecutiveIntelligenceService(request)
        # Use the built-in analytics context from the request scope if available
        full_context = dict(context)
        full_context.setdefault("analytics", analytics)
        result = await service.answer_question(body.message, full_context)
        if not isinstance(result, dict):
            result = {"response": str(result)}
        result.setdefault("analyticsUsed", _derive_analytics_used(body.message, analytics))
        return ChatResponse(**result)
    except NotImplementedError:
        result = generate_local_chat_response(body.message, context.get("analytics", {}))
        return ChatResponse(**result)
    except Exception as e:
        result = generate_local_chat_response(body.message, context.get("analytics", {}))
        result["response"] = "I encountered an error. Showing local analytics summary."
        return ChatResponse(**result)


# ============================================================
# FIR Intelligence
# ============================================================

@router.post(
    "/fir-intelligence",
    response_model=FIRIntelligenceResponse,
    summary="FIR Intelligence Analysis",
    description="Analyze an uploaded FIR and extract structured intelligence.",
)
async def fir_intelligence(
    request: Request,
    payload: Dict[str, Any] = Body(...),
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_AI_INVESTIGATION])),
):
    try:
        if not ExecutiveIntelligenceService._is_ai_available():
            result = generate_local_fir_intelligence(payload)
            return FIRIntelligenceResponse(**result)

        service = ExecutiveIntelligenceService(request)
        result = await service.analyze_fir(payload)
        if not isinstance(result, dict):
            raise HTTPException(status_code=500, detail="Invalid AI response")
        result.setdefault("generatedAt", _now_iso())
        result.setdefault("isFallback", False)
        return FIRIntelligenceResponse(**result)
    except NotImplementedError:
        result = generate_local_fir_intelligence(payload)
        return FIRIntelligenceResponse(**result)
    except Exception as e:
        result = generate_local_fir_intelligence(payload)
        return FIRIntelligenceResponse(**result)


# ============================================================
# Crime Pattern Discovery
# ============================================================

@router.post(
    "/patterns",
    response_model=PatternDiscoveryResponse,
    summary="Crime Pattern Discovery",
    description="Detect hidden correlations across time, location, offender, and crime category.",
)
async def pattern_discovery(
    request: Request,
    payload: Dict[str, Any] = Body(...),
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_AI_INVESTIGATION])),
):
    try:
        analytics = payload.get("analytics", {})

        if not ExecutiveIntelligenceService._is_ai_available():
            result = generate_local_patterns(analytics)
            return PatternDiscoveryResponse(**result)

        service = ExecutiveIntelligenceService(request)
        result = await service.predict_emerging_threats(analytics)
        if not isinstance(result, dict):
            raise HTTPException(status_code=500, detail="Invalid AI response")
        result.setdefault("generatedAt", _now_iso())
        result.setdefault("isFallback", False)
        return PatternDiscoveryResponse(**result)
    except NotImplementedError:
        result = generate_local_patterns(payload.get("analytics", {}))
        return PatternDiscoveryResponse(**result)
    except Exception as e:
        result = generate_local_patterns(payload.get("analytics", {}))
        return PatternDiscoveryResponse(**result)


# ============================================================
# Recommendation Engine
# ============================================================

@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    summary="Operational Recommendations",
    description="Generate patrol deployment, investigation priority, surveillance, checkpoint, and resource allocation recommendations.",
)
async def recommendations(
    request: Request,
    payload: Dict[str, Any] = Body(...),
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_AI_INVESTIGATION])),
):
    try:
        analytics = payload.get("analytics", {})

        if not ExecutiveIntelligenceService._is_ai_available():
            result = generate_local_recommendations(analytics)
            return RecommendationResponse(**result)

        service = ExecutiveIntelligenceService(request)
        result = await service.generate_recommendations(analytics)
        if not isinstance(result, dict):
            raise HTTPException(status_code=500, detail="Invalid AI response")
        result.setdefault("generatedAt", _now_iso())
        result.setdefault("isFallback", False)
        return RecommendationResponse(**result)
    except NotImplementedError:
        result = generate_local_recommendations(payload.get("analytics", {}))
        return RecommendationResponse(**result)
    except Exception as e:
        result = generate_local_recommendations(payload.get("analytics", {}))
        return RecommendationResponse(**result)


# ============================================================
# AI Report Generator
# ============================================================

@router.post(
    "/report",
    response_model=IntelligenceReportResponse,
    summary="AI Intelligence Report",
    description="Generate a structured intelligence report using dashboard analytics.",
)
async def intelligence_report(
    request: Request,
    payload: Dict[str, Any] = Body(...),
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_AI_INVESTIGATION])),
):
    try:
        if not ExecutiveIntelligenceService._is_ai_available():
            result = generate_local_intelligence_report(payload)
            return IntelligenceReportResponse(**result)

        service = ExecutiveIntelligenceService(request)
        result = await service.generate_intelligence_report(payload)
        if not isinstance(result, dict):
            raise HTTPException(status_code=500, detail="Invalid AI response")
        result.setdefault("generatedAt", _now_iso())
        result.setdefault("isFallback", False)
        return IntelligenceReportResponse(**result)
    except NotImplementedError:
        result = generate_local_intelligence_report(payload)
        return IntelligenceReportResponse(**result)
    except Exception as e:
        result = generate_local_intelligence_report(payload)
        return IntelligenceReportResponse(**result)


# ============================================================
# Explain With AI
# ============================================================

@router.post(
    "/explain",
    response_model=ExplanationResponse,
    summary="Explain Dashboard Chart/Map",
    description="AI explanation for why a pattern exists and what action to take.",
)
async def explain_with_ai(
    request: Request,
    payload: Dict[str, Any] = Body(...),
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_AI_INVESTIGATION])),
):
    try:
        chart_type = payload.get("chart_type", "")
        data = payload.get("data", {})
        filters = payload.get("filters", {})

        result = generate_local_explanation(chart_type, data, filters)
        return ExplanationResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate explanation: {str(e)}",
        )


# ============================================================
# Evidence Summarizer
# ============================================================

@router.post(
    "/evidence-summary",
    response_model=EvidenceSummaryResponse,
    summary="Evidence Summarizer",
    description="Summarize uploaded FIRs, witness statements, and complaint documents into structured intelligence.",
)
async def evidence_summary(
    request: Request,
    payload: Dict[str, Any] = Body(...),
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_AI_INVESTIGATION])),
):
    try:
        document_type = payload.get("document_type", "unknown")
        content = payload.get("content", "")

        if not ExecutiveIntelligenceService._is_ai_available():
            result = generate_local_evidence_summary(document_type, content)
            return EvidenceSummaryResponse(**result)

        service = ExecutiveIntelligenceService(request)
        result = await service._evidence_summary(document_type, content)
        if not isinstance(result, dict):
            raise HTTPException(status_code=500, detail="Invalid AI response")
        result.setdefault("generatedAt", _now_iso())
        result.setdefault("isFallback", False)
        return EvidenceSummaryResponse(**result)
    except NotImplementedError:
        result = generate_local_evidence_summary(
            payload.get("document_type", "unknown"),
            payload.get("content", ""),
        )
        return EvidenceSummaryResponse(**result)
    except Exception as e:
        result = generate_local_evidence_summary(
            payload.get("document_type", "unknown"),
            payload.get("content", ""),
        )
        return EvidenceSummaryResponse(**result)


# ============================================================
# Timeline Generator
# ============================================================

@router.post(
    "/timeline",
    response_model=TimelineResponse,
    summary="Incident Timeline Generator",
    description="Convert incident descriptions into chronological investigative timelines.",
)
async def timeline_generator(
    request: Request,
    payload: Dict[str, Any] = Body(...),
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.ACCESS_AI_INVESTIGATION])),
):
    try:
        incident_description = payload.get("incident_description", "")

        if not ExecutiveIntelligenceService._is_ai_available():
            result = generate_local_timeline(incident_description)
            return TimelineResponse(**result)

        service = ExecutiveIntelligenceService(request)
        result = await service._generate_timeline(incident_description)
        if not isinstance(result, dict):
            raise HTTPException(status_code=500, detail="Invalid AI response")
        result.setdefault("generatedAt", _now_iso())
        result.setdefault("isFallback", False)
        return TimelineResponse(**result)
    except NotImplementedError:
        result = generate_local_timeline(payload.get("incident_description", ""))
        return TimelineResponse(**result)
    except Exception as e:
        result = generate_local_timeline(payload.get("incident_description", ""))
        return TimelineResponse(**result)


# ============================================================
# Helpers
# ============================================================

def _derive_analytics_used(question: str, analytics: Dict[str, Any]) -> List[str]:
    """Infer which analytics sources were used based on the question keywords."""
    lower = question.lower()
    mapping = {
        "hotspot": "hotspots",
        "trend": "crime_trends",
        "district": "district_statistics",
        "anomal": "alerts",
        "alert": "alerts",
        "network": "network_analysis_summary",
        "repeat offender": "repeat_offender_statistics",
        "risk": "risk_scores",
        "kpi": "kpi_metrics",
    }
    used = []
    for keyword, source in mapping.items():
        if keyword in lower and source in analytics:
            used.append(source)
    return used or ["dashboard_analytics"]


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
