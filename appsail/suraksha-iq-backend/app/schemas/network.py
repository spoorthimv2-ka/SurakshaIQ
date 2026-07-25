from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional

class NetworkNode(BaseModel):
    id: str
    label: str
    type: str  # Offender, Crime, FIR, PoliceStation, District
    properties: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)

class NetworkEdge(BaseModel):
    source: str
    target: str
    type: str  # committed, registered_in, investigated_by, occurred_at, belongs_to, co_offender, family, phone, vehicle, related_to, operates_in, known_at, uses
    properties: Dict[str, Any] = {}
    strength: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class NetworkStatistics(BaseModel):
    total_nodes: int
    total_edges: int
    connected_offenders: int
    connected_stations: int
    connected_districts: int
    average_connections: float

    model_config = ConfigDict(from_attributes=True)

class NetworkGraphResponse(BaseModel):
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]
    statistics: NetworkStatistics
    metadata: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)

class NetworkSearchResponse(BaseModel):
    query: str
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]

    model_config = ConfigDict(from_attributes=True)

class NetworkFilters(BaseModel):
    crime_category: Optional[str] = None
    district_id: Optional[str] = None
    station_id: Optional[str] = None
    time_period: Optional[str] = None
    relationship_type: Optional[str] = None
    risk_level: Optional[str] = None
    active_investigations: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class AdvancedGraphResponse(BaseModel):
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]
    statistics: NetworkStatistics
    communities: List[Dict[str, Any]] = []
    centrality: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)

class NetworkAnalyticsResponse(BaseModel):
    community_stats: Dict[str, Any] = {}
    central_actors: List[Dict[str, Any]] = []
    most_connected: List[Dict[str, Any]] = []
    highest_risk_cluster: Dict[str, Any] = {}
    bridge_nodes: List[Dict[str, Any]] = []
    cluster_summaries: List[Dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True)

class NetworkTimelineResponse(BaseModel):
    timeline: List[Dict[str, Any]] = []
    min_date: Optional[str] = None
    max_date: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class CommunityDetectionResponse(BaseModel):
    communities: List[Dict[str, Any]] = []
    community_count: int = 0
    modularity: float = 0.0

    model_config = ConfigDict(from_attributes=True)

class CentralActorResponse(BaseModel):
    actors: List[Dict[str, Any]] = []
    metric: str = "degree"

    model_config = ConfigDict(from_attributes=True)
