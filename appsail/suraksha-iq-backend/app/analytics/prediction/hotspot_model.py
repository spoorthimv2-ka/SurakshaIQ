from typing import List, Dict
from app.schemas.hotspot import HotspotCluster
from app.schemas.prediction import PredictedHotspot

def predict_hotspots(
    current_clusters: List[HotspotCluster], 
    past_clusters: List[HotspotCluster] = None,
    timeframe_days: int = 7
) -> List[PredictedHotspot]:
    """
    Predicts future hotspots using a statistical momentum approach.
    Compares current clusters against past clusters to project future intensity.
    """
    past_map: Dict[str, HotspotCluster] = {c.id: c for c in (past_clusters or [])}
    
    predictions = []
    for current in current_clusters:
        past = past_map.get(current.id)
        
        # Default momentum is 1.0 (flat). If it existed in the past, calculate ratio.
        momentum = 1.0
        factors = []
        confidence = 60.0 # Base confidence
        
        if past:
            # If crime count grew, momentum > 1
            if past.crime_count > 0:
                momentum = current.crime_count / past.crime_count
            
            if momentum > 1.2:
                factors.append(f"Recent surge in crimes (up {int((momentum-1)*100)}%)")
                confidence = 85.0
            elif momentum < 0.8:
                factors.append("Crime count is declining locally")
                confidence = 75.0
            else:
                factors.append("Consistent, stable historical crime rate")
                confidence = 90.0
        else:
            factors.append("Newly emerged cluster, no long-term historical baseline")
            momentum = 1.1 # Assume slight growth for new clusters
            
        # Add primary crime types as factors
        if current.primary_crime_types:
            factors.append(f"Driven by: {', '.join(current.primary_crime_types)}")
            
        # Project intensity
        predicted_intensity = min(current.intensity_score * momentum, 100.0)
        
        # Project radius slightly based on momentum
        predicted_radius = current.radius_meters * (1.0 + (momentum - 1.0) * 0.1)
        
        predictions.append(PredictedHotspot(
            id=current.id,
            latitude=current.latitude,
            longitude=current.longitude,
            predicted_radius_meters=round(predicted_radius, 2),
            predicted_intensity_score=round(predicted_intensity, 1),
            confidence_score=round(confidence, 1),
            predicted_timeframe_days=timeframe_days,
            contributing_factors=factors
        ))
        
    return sorted(predictions, key=lambda x: x.predicted_intensity_score, reverse=True)
