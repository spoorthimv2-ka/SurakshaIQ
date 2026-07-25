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
    analyticsUsed: List[str] = []
    model: Optional[str] = None

    model_config = {"from_attributes": True}


class RecommendationItem(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    category: str = "operational"

    model_config = {"from_attributes": True}


class SummaryResponse(BaseModel):
    overallRisk: str
    executiveSummary: str
    keyFindings: List[str]
    recommendedActions: List[str]
    confidence: float
    generatedAt: str
    isFallback: bool = False
    analyticsUsed: List[str] = []
    model: Optional[str] = None

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    response: str
    confidence: float = 0.0
    analyticsUsed: List[str] = []
    isFallback: bool = False
    model: Optional[str] = None

    model_config = {"from_attributes": True}


class FIRIntelligenceResponse(BaseModel):
    crime_category: str
    severity: str
    modus_operandi: str
    entities: Dict[str, List[str]] = {}
    investigation_suggestions: List[str] = []
    confidence: float = Field(..., ge=0, le=1)
    generatedAt: str
    isFallback: bool = False
    analyticsUsed: List[str] = []
    model: Optional[str] = None

    model_config = {"from_attributes": True}


class PatternDiscoveryResponse(BaseModel):
    patterns: List[Dict[str, Any]] = []
    correlations: List[Dict[str, Any]] = []
    confidence: float = Field(..., ge=0, le=1)
    generatedAt: str
    isFallback: bool = False
    analyticsUsed: List[str] = []
    model: Optional[str] = None

    model_config = {"from_attributes": True}


class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]] = []
    overall_risk: str = "Medium"
    confidence: float = Field(..., ge=0, le=1)
    generatedAt: str
    isFallback: bool = False
    analyticsUsed: List[str] = []
    model: Optional[str] = None

    model_config = {"from_attributes": True}


class IntelligenceReportResponse(BaseModel):
    reportId: str
    title: str
    content: str
    format: str = "text"
    sections: List[Dict[str, Any]] = []
    confidence: float = Field(..., ge=0, le=1)
    generatedAt: str
    isFallback: bool = False
    analyticsUsed: List[str] = []
    model: Optional[str] = None

    model_config = {"from_attributes": True}


class ExplanationResponse(BaseModel):
    explanation: str
    confidence: float = Field(..., ge=0, le=1)
    generatedAt: str
    isFallback: bool = False
    analyticsUsed: List[str] = []
    model: Optional[str] = None

    model_config = {"from_attributes": True}


class EvidenceSummaryResponse(BaseModel):
    summary: str
    extracted_entities: Dict[str, List[str]] = {}
    key_points: List[str] = []
    confidence: float = Field(..., ge=0, le=1)
    generatedAt: str
    isFallback: bool = False
    analyticsUsed: List[str] = []
    model: Optional[str] = None

    model_config = {"from_attributes": True}


class TimelineResponse(BaseModel):
    events: List[Dict[str, Any]] = []
    narrative: str = ""
    confidence: float = Field(..., ge=0, le=1)
    generatedAt: str
    isFallback: bool = False
    analyticsUsed: List[str] = []
    model: Optional[str] = None

    model_config = {"from_attributes": True}
