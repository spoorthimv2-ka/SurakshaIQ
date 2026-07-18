from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime

class AnomalyResult(BaseModel):
    id: str
    anomaly_type: str # e.g. "CRIME_SPIKE"
    severity: str # HIGH, MEDIUM, LOW
    affected_scope: str # e.g. "DISTRICT: D1"
    description: str
    detection_timestamp: datetime
    related_entity_id: str

    model_config = ConfigDict(from_attributes=True)

class AnomalyDetectionResponse(BaseModel):
    anomalies: List[AnomalyResult]
    model_version: str = "v1.0-statistical-deviation"

    model_config = ConfigDict(from_attributes=True)
