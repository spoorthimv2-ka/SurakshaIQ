from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import Any, Dict

from app.api.deps import get_current_officer
from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    ExecutiveIntelligenceResponse,
    SummaryResponse,
)
from app.services.ai_service import ExecutiveIntelligenceService

router = APIRouter()


@router.post(
    "/summary",
    response_model=ExecutiveIntelligenceResponse,
    summary="Executive Intelligence Summary",
    description="Generate an executive intelligence briefing from dashboard analytics.",
)
async def executive_summary(
    request: Request,
    payload: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_officer),
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


@router.post(
    "/recommendations",
    response_model=SummaryResponse,
    summary="Executive Recommendations",
    description="Generate operational recommendations from dashboard analytics.",
)
async def executive_recommendations(
    request: Request,
    payload: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    try:
        service = ExecutiveIntelligenceService(request)
        result = await service.generate_recommendations(payload.get("dashboard_payload", {}))
        return SummaryResponse(
            overallRisk=result.get("overallRisk", "Medium"),
            executiveSummary="Operational recommendations generated.",
            keyFindings=[],
            recommendedActions=result,
            confidence=float(result.get("confidence") or 0.7),
            generatedAt=result.get("generatedAt", _now_iso()),
            isFallback=result.get("isFallback", True),
        )
    except NotImplementedError as e:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}",
        )


@router.post(
    "/report",
    response_model=Dict[str, Any],
    summary="Intelligence Report",
    description="Generate an intelligence report.",
)
async def intelligence_report(
    request: Request,
    payload: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    try:
        service = ExecutiveIntelligenceService(request)
        result = await service.generate_intelligence_report(payload)
        return result
    except NotImplementedError as e:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}",
        )


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="AI Chat",
    description="Chat with the AI assistant.",
)
async def ai_chat(
    request: Request,
    body: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    try:
        service = ExecutiveIntelligenceService(request)
        result = await service.answer_question(body.message, body.context)
        return ChatResponse(response=result.get("response", ""))
    except NotImplementedError as e:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}",
        )
