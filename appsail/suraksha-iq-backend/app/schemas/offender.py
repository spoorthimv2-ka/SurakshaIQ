from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class OffenderSummary(BaseModel):
    offender_id: str
    name: str
    risk_classification: str  # e.g., HIGH, MEDIUM, LOW
    offense_count: int
    associated_case_ids: List[str]
    last_known_location: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class RepeatOffenderResponse(BaseModel):
    data: List[OffenderSummary]
    total: int
    page: int
    size: int

    model_config = ConfigDict(from_attributes=True)
