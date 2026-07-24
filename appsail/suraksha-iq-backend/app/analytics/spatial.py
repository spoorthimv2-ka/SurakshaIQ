from typing import List, Dict, Any, Optional
from math import radians, sin, cos, sqrt, atan2
from pydantic import BaseModel


class Point(BaseModel):
    crime_id: str
    latitude: float
    longitude: float
    incident_date: str
    crime_type: str
    district_id: str
    station_id: str
    properties: Dict[str, Any] = {}


class Cluster(BaseModel):
    cluster_id: str
    center_lat: float
    center_lon: float
    radius_m: float
    point_count: int
    crime_types: List[str]
    district_id: str
    station_id: str
    period_start: str
    period_end: str


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometers between two WGS84 points."""
    R = 6371.0
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def dbscan_cluster(points: List[Point], eps_km: float = 0.5, min_samples: int = 3) -> List[Cluster]:
    """Density-based spatial clustering of crime points using haversine metric."""
    if not points:
        return []

    n = len(points)
    visited = [False] * n
    cluster_labels = [-1] * n
    cluster_id = 0

    def region_query(idx: int) -> List[int]:
        neighbors = []
        for i in range(n):
            if i != idx:
                dist = haversine_km(
                    points[idx].latitude, points[idx].longitude,
                    points[i].latitude, points[i].longitude,
                )
                if dist <= eps_km:
                    neighbors.append(i)
        return neighbors

    def expand_cluster(idx: int, neighbors: List[int], cid: int) -> None:
        cluster_labels[idx] = cid
        i = 0
        while i < len(neighbors):
            j = neighbors[i]
            if not visited[j]:
                visited[j] = True
                new_neighbors = region_query(j)
                if len(new_neighbors) >= min_samples:
                    neighbors.extend(new_neighbors)
            if cluster_labels[j] == -1:
                cluster_labels[j] = cid
            i += 1

    for i in range(n):
        if visited[i]:
            continue
        visited[i] = True
        neighbors = region_query(i)
        if len(neighbors) < min_samples:
            cluster_labels[i] = -1  # noise
        else:
            expand_cluster(i, neighbors, cluster_id)
            cluster_id += 1

    clusters: Dict[int, List[int]] = {}
    for i, label in enumerate(cluster_labels):
        if label != -1:
            clusters.setdefault(label, []).append(i)

    results: List[Cluster] = []
    for label, indices in clusters.items():
        members = [points[i] for i in indices]
        lats = [p.latitude for p in members]
        lons = [p.longitude for p in members]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        radius_m = max(
            haversine_km(center_lat, center_lon, p.latitude, p.longitude) for p in members
        ) * 1000.0
        crime_types = list({p.crime_type for p in members})
        period_start = min(p.incident_date for p in members)
        period_end = max(p.incident_date for p in members)
        district_id = members[0].district_id
        station_id = members[0].station_id

        results.append(
            Cluster(
                cluster_id=f"CLUSTER-{label}",
                center_lat=center_lat,
                center_lon=center_lon,
                radius_m=radius_m,
                point_count=len(members),
                crime_types=crime_types,
                district_id=district_id,
                station_id=station_id,
                period_start=period_start,
                period_end=period_end,
            )
        )

    return sorted(results, key=lambda c: c.point_count, reverse=True)


def compute_clusters(crimes: List[Dict[str, Any]], eps_km: float = 0.5, min_samples: int = 3) -> List[Cluster]:
    """Convert raw crime dicts to Points, run DBSCAN, return clusters."""
    points: List[Point] = []
    for c in crimes:
        lat = c.get("latitude")
        lon = c.get("longitude")
        if lat is None or lon is None:
            continue
        points.append(
            Point(
                crime_id=c.get("ROWID", ""),
                latitude=float(lat),
                longitude=float(lon),
                incident_date=str(c.get("incident_date", c.get("CREATEDTIME", "")))[:10],
                crime_type=c.get("crime_type", "UNKNOWN"),
                district_id=c.get("district_id", "UNKNOWN"),
                station_id=c.get("station_id", "UNKNOWN"),
                properties=c,
            )
        )
    return dbscan_cluster(points, eps_km=eps_km, min_samples=min_samples)
