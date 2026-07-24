from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List

class SearchResult(BaseModel):
    id: str
    category: str
    title: str
    subtitle: str
    description: str
    relevance_score: float
    created_at: str
    metadata: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResult]
    filters_applied: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)

class SearchSuggestion(BaseModel):
    keyword: str
    category: str
    count: int

    model_config = ConfigDict(from_attributes=True)

class SearchFilters(BaseModel):
    categories: List[Dict[str, Any]]
    districts: List[Dict[str, Any]]
    stations: List[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)
