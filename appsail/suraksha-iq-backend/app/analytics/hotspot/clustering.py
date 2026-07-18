from typing import List, Dict, Any
from app.models.crime import Crime
from app.schemas.hotspot import HotspotCluster
from collections import defaultdict

def generate_grid_clusters(crimes: List[Crime], grid_precision: int = 2) -> List[HotspotCluster]:
    """
    Generates a basic grid-based clustering for crimes.
    `grid_precision = 2` roughly translates to ~1.1km grid at the equator.
    """
    clusters_map: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "lat_sum": 0.0,
        "lon_sum": 0.0,
        "crime_count": 0,
        "crime_types": defaultdict(int)
    })

    for crime in crimes:
        if crime.latitude is None or crime.longitude is None:
            continue
            
        grid_lat = round(crime.latitude, grid_precision)
        grid_lon = round(crime.longitude, grid_precision)
        grid_key = f"{grid_lat}_{grid_lon}"
        
        clusters_map[grid_key]["lat_sum"] += crime.latitude
        clusters_map[grid_key]["lon_sum"] += crime.longitude
        clusters_map[grid_key]["crime_count"] += 1
        clusters_map[grid_key]["crime_types"][crime.crime_type] += 1

    results = []
    for key, data in clusters_map.items():
        count = data["crime_count"]
        # Calculate centroid
        centroid_lat = data["lat_sum"] / count
        centroid_lon = data["lon_sum"] / count
        
        # Sort crime types by frequency
        sorted_types = sorted(data["crime_types"].items(), key=lambda x: x[1], reverse=True)
        primary_types = [t[0] for t in sorted_types[:3]]
        
        # Fake a radius (e.g. 500m + 50m per crime) for UI representation, since it's a grid
        radius = 500.0 + (min(count, 100) * 10)
        
        # Simple intensity score out of 100
        intensity = min((count / 10.0) * 100, 100.0)
        
        results.append(HotspotCluster(
            id=key,
            latitude=centroid_lat,
            longitude=centroid_lon,
            radius_meters=radius,
            intensity_score=round(intensity, 1),
            crime_count=count,
            primary_crime_types=primary_types
        ))
        
    # Return highest intensity first
    return sorted(results, key=lambda x: x.intensity_score, reverse=True)
