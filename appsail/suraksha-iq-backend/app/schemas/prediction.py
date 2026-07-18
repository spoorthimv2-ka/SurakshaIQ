from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class PredictedHotspot(BaseModel):
    id: str
    latitude: float
    longitude: float
    predicted_radius_meters: float
    predicted_intensity_score: float
    confidence_score: float  # 0 to 100
    predicted_timeframe_days: int
    contributing_factors: List[str]

    model_config = ConfigDict(from_attributes=True)

class HotspotPredictionResponse(BaseModel):
    predictions: List[PredictedHotspot]
    model_version: str = "v1.0-statistical-momentum"

    model_config = ConfigDict(from_attributes=True)
