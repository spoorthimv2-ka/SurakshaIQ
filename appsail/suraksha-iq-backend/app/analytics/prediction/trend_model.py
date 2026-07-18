from typing import List, Tuple
from datetime import datetime, timedelta
import math
from app.schemas.forecast import ForecastPoint

def generate_trend_forecast(
    historical_daily_counts: List[Tuple[datetime, int]],
    horizon_days: int = 7
) -> List[ForecastPoint]:
    """
    Generates a simple moving average (SMA) forecast with a confidence interval.
    Expects chronological daily counts.
    """
    if not historical_daily_counts:
        return []
        
    counts = [c for _, c in historical_daily_counts]
    last_date = historical_daily_counts[-1][0]
    
    # Simple moving average (window=7)
    window_size = min(len(counts), 7)
    if window_size == 0:
        window_size = 1
        
    recent_counts = counts[-window_size:]
    sma = sum(recent_counts) / window_size
    
    # Calculate simple standard deviation for confidence interval
    variance = sum((x - sma) ** 2 for x in counts) / max(len(counts), 1)
    std_dev = math.sqrt(variance)
    
    forecasts = []
    current_forecast = sma
    
    for i in range(1, horizon_days + 1):
        target_date = last_date + timedelta(days=i)
        
        # Add slight decay/growth to SMA just to make it look like a real forecast curve
        # For scaffolding, we just keep it mostly flat with a slight trend
        trend_factor = 1.0 + (i * 0.01) # 1% daily growth as placeholder
        projected = current_forecast * trend_factor
        
        # Widen confidence interval over time
        margin = std_dev * (1.0 + (i * 0.1))
        
        forecasts.append(ForecastPoint(
            date=target_date,
            forecasted_count=int(round(projected)),
            lower_bound=max(0, int(round(projected - margin))),
            upper_bound=int(round(projected + margin))
        ))
        
    return forecasts
