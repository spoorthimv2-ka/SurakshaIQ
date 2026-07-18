from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional

class Node(BaseModel):
    id: str
    label: str
    type: str # e.g. "Offender", "Crime", "Location"
    properties: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)

class Link(BaseModel):
    source: str
    target: str
    type: str # e.g. "COMMITTED", "OCCURRED_AT", "ASSOCIATED_WITH"
    properties: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)

class NetworkGraphResponse(BaseModel):
    nodes: List[Node]
    links: List[Link]
    centrality_metrics: Optional[Dict[str, float]] = None

    model_config = ConfigDict(from_attributes=True)
