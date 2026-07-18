from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime

class ForecastPoint(BaseModel):
    date: datetime
    forecasted_count: int
    lower_bound: int
    upper_bound: int

    model_config = ConfigDict(from_attributes=True)

class ForecastResponse(BaseModel):
    category: str # e.g. "total_crimes"
    horizon_days: int
    data: List[ForecastPoint]
    methodology: str = "v1.0-sma-extrapolation"

    model_config = ConfigDict(from_attributes=True)
