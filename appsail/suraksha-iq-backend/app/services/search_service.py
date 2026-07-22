from typing import Any, Dict, List, Optional
from fastapi import Request
from app.repositories.search_repo import SearchRepository
from app.schemas.search import SearchResult, SearchResponse, SearchSuggestion, SearchFilters
from app.core.logger import logger
from app.core.exceptions import DataValidationError, RepositoryError

class SearchService:
    """Service layer for global search."""

    CATEGORY_LABELS = {
        "Crime": "Crimes",
        "FIR": "FIRs",
        "Hotspot": "Hotspots",
        "RepeatOffender": "Repeat Offenders",
        "Network": "Network Entities",
        "PredictiveRisk": "Predictive Risk",
        "Anomaly": "Anomalies",
        "Alert": "Alerts",
        "Report": "Reports",
    }

    def __init__(self, request: Request, repo: SearchRepository):
        self.request = request
        self.repo = repo

    async def search(
        self,
        keyword: str,
        category: Optional[str] = None,
        district_id: Optional[str] = None,
        station_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Performs global search across all entities."""
        logger.info(f"Searching for keyword: {keyword}, category: {category}, district: {district_id}, station: {station_id}")
        if not keyword:
            raise DataValidationError("Search keyword is required")

        categories = [category] if category else list(self.CATEGORY_LABELS.keys())
        raw_results: List[Dict[str, Any]] = []

        for cat in categories:
            try:
                cat_results = await self._search_category(cat, keyword, district_id, station_id, limit)
                raw_results.extend(cat_results)
            except RepositoryError as e:
                logger.warning(f"Search failed for category {cat}: {e}")
                continue

        scored = self._score_results(raw_results, keyword)
        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        total = len(scored)
        paged = scored[offset : offset + limit]

        results = [SearchResult(**r) for r in paged]
        return {
            "query": keyword,
            "total_results": total,
            "results": results,
            "filters_applied": {
                "category": category,
                "district_id": district_id,
                "station_id": station_id,
            },
        }

    async def get_suggestions(self, keyword: str, limit: int = 10) -> List[Dict[str, str]]:
        """Returns top matching keywords as suggestions."""
        logger.info(f"Fetching suggestions for keyword: {keyword}")
        if not keyword:
            return []

        suggestions: List[Dict[str, str]] = []
        seen = set()

        try:
            crimes = await self.repo.search_crimes(keyword, limit=limit)
            for c in crimes:
                title = c.get("title", "")
                if title and title.lower() not in seen:
                    seen.add(title.lower())
                    suggestions.append({"keyword": title, "category": "Crime", "count": 1})
        except RepositoryError:
            pass

        try:
            firs = await self.repo.search_firs(keyword, limit=limit)
            for f in firs:
                num = f.get("fir_number", "")
                if num and num.lower() not in seen:
                    seen.add(num.lower())
                    suggestions.append({"keyword": num, "category": "FIR", "count": 1})
        except RepositoryError:
            pass

        try:
            offenders = await self.repo.search_repeat_offenders(keyword, limit=limit)
            for o in offenders:
                name = o.get("name", "")
                if name and name.lower() not in seen:
                    seen.add(name.lower())
                    suggestions.append({"keyword": name, "category": "RepeatOffender", "count": 1})
        except RepositoryError:
            pass

        try:
            alerts = await self.repo.search_alerts(keyword, limit=limit)
            for a in alerts:
                title = a.get("title", "")
                if title and title.lower() not in seen:
                    seen.add(title.lower())
                    suggestions.append({"keyword": title, "category": "Alert", "count": 1})
        except RepositoryError:
            pass

        suggestions.sort(key=lambda x: x["keyword"].lower())
        return suggestions[:limit]

    async def get_filters(self) -> Dict[str, Any]:
        """Returns available filter options."""
        logger.info("Fetching search filters")
        try:
            districts = await self.repo.get_districts()
            stations = await self.repo.get_stations()
            return {
                "categories": [
                    {"id": k, "label": v} for k, v in self.CATEGORY_LABELS.items()
                ],
                "districts": [
                    {"id": d.get("ROWID", ""), "name": d.get("name", "")} for d in districts
                ],
                "stations": [
                    {"id": s.get("ROWID", ""), "name": s.get("name", ""), "district_id": s.get("district_id", "")}
                    for s in stations
                ],
            }
        except RepositoryError as e:
            logger.error(f"Error fetching search filters: {e}")
            raise

    async def _search_category(
        self,
        category: str,
        keyword: str,
        district_id: Optional[str],
        station_id: Optional[str],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Searches a specific category."""
        if category == "Crime":
            return await self.repo.search_crimes(keyword, district_id, station_id, limit)
        if category == "FIR":
            return await self.repo.search_firs(keyword, district_id, station_id, limit)
        if category == "Hotspot":
            return await self.repo.search_hotspots(keyword, district_id, limit)
        if category == "RepeatOffender":
            return await self.repo.search_repeat_offenders(keyword, limit)
        if category == "Network":
            return await self.repo.search_network_nodes(keyword, limit)
        if category == "PredictiveRisk":
            return await self.repo.search_risk_predictions(keyword, district_id, limit)
        if category == "Anomaly":
            return await self.repo.search_anomalies(keyword, limit)
        if category == "Alert":
            return await self.repo.search_alerts(keyword, limit)
        if category == "Report":
            return await self.repo.search_reports(keyword, limit)
        return []

    def _score_results(self, results: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
        """Scores and transforms raw results into SearchResult format."""
        scored: List[Dict[str, Any]] = []
        kw_lower = keyword.lower()

        for r in results:
            category = r.get("_category", "Unknown")
            title = r.get("title", r.get("name", r.get("label", "Untitled")))
            subtitle = r.get("subtitle", r.get("crime_type", r.get("fir_number", category)))
            description = r.get("description", r.get("location", ""))
            created_at = r.get("CREATEDTIME", r.get("created_at", ""))

            title_lower = title.lower()
            desc_lower = description.lower()

            score = 0.0
            if title_lower == kw_lower:
                score += 100.0
            elif title_lower.startswith(kw_lower):
                score += 75.0
            elif kw_lower in title_lower:
                score += 50.0

            if desc_lower == kw_lower:
                score += 50.0
            elif kw_lower in desc_lower:
                score += 25.0

            if score > 0:
                scored.append({
                    "id": r.get("ROWID", r.get("id", "")),
                    "category": category,
                    "title": title,
                    "subtitle": subtitle,
                    "description": description,
                    "relevance_score": score,
                    "created_at": created_at,
                    "metadata": {k: v for k, v in r.items() if k not in {"_category", "title", "description", "CREATEDTIME", "ROWID", "id"}},
                })

        return scored
