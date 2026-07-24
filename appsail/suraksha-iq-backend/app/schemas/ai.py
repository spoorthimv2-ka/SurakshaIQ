from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class ExecutiveIntelligenceResponse(BaseModel):
    overallRisk: str = Field(..., description="High | Medium | Low")
    executiveSummary: str
    keyFindings: List[str]
    recommendedActions: List[str]
    confidence: float = Field(..., ge=0, le=1)
    generatedAt: str
    isFallback: bool = False

class RecommendationItem(BaseModel):
    title: str
    description: str
    priority: str = "medium"

class SummaryResponse(BaseModel):
    overallRisk: str
    executiveSummary: str
    keyFindings: List[str]
    recommendedActions: List[str]
    confidence: float
    generatedAt: str
    isFallback: bool = False

    model_config = {"from_attributes": True}

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
