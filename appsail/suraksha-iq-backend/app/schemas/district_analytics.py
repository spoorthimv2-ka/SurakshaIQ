from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class DistrictTrend(BaseModel):
    district_id: str
    district_name: str
    current_count: int
    trend_direction: str # "UP", "DOWN", "FLAT"
    trend_percentage: float

class DistrictRollupResponse(BaseModel):
    district_id: str
    district_name: str
    total_crimes: int
    comparisons: Optional[List[DistrictTrend]] = None

    model_config = ConfigDict(from_attributes=True)
