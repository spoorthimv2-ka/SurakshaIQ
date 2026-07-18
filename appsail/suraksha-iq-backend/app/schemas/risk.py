from pydantic import BaseModel, ConfigDict
from typing import List

class RiskScoreResponse(BaseModel):
    entity_id: str
    entity_type: str  # e.g., "OFFENDER"
    risk_score: float # 0 to 100
    risk_classification: str # HIGH, MEDIUM, LOW
    contributing_factors: List[str]
    methodology: str = "v1.0-frequency-based"

    model_config = ConfigDict(from_attributes=True)
