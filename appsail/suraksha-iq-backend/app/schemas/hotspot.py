from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class HotspotCluster(BaseModel):
    id: str  # e.g., grid cell id or hash
    latitude: float
    longitude: float
    radius_meters: float
    intensity_score: float
    crime_count: int
    primary_crime_types: List[str]

    model_config = ConfigDict(from_attributes=True)

class HotspotResponse(BaseModel):
    clusters: List[HotspotCluster]
    start_date: datetime
    end_date: datetime

    model_config = ConfigDict(from_attributes=True)
