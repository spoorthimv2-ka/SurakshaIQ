from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import Request

from app.repositories.crime_repo import CrimeRepository
from app.repositories.base_repository import BaseCatalystRepository
from app.analytics.spatial import compute_clusters, Cluster


class HotspotEngine:
    """Application-layer spatial clustering against Catalyst Data Store."""

    def __init__(self, request: Request):
        self.request = request
        self.crime_repo = CrimeRepository(request)
        self.cluster_repo = BaseCatalystRepository(request, table_name="CrimeHotspotCluster")

    async def run_clustering(
        self,
        eps_km: float = 0.5,
        min_samples: int = 3,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[Cluster]:
        """Read crimes from Catalyst, run DBSCAN, write clusters back to Catalyst."""
        crimes = await self.crime_repo.find_filtered(
            date_from=date_from,
            date_to=date_to,
            limit=5000,
        )
        clusters = compute_clusters(crimes, eps_km=eps_km, min_samples=min_samples)

        for c in clusters:
            row = c.model_dump(mode="json")
            row["scored_at"] = datetime.now(timezone.utc).isoformat()
            self.cluster_repo.get_table().insert_row(row)

        return clusters

    async def get_cached_clusters(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[Cluster]:
        """Read previously computed clusters from Catalyst."""
        try:
            query = f"SELECT * FROM {self.cluster_repo.table_name} ORDER BY scored_at DESC LIMIT 1000"
            result = self.cluster_repo.zcql.execute_query(query)
            rows = []
            for item in result:
                if self.cluster_repo.table_name in item:
                    rows.append(item[self.cluster_repo.table_name])
            return [Cluster(**r) for r in rows]
        except Exception:
            return []
