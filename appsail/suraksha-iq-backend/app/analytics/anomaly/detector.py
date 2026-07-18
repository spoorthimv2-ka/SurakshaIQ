from typing import List, Tuple
from datetime import datetime, timezone
import math
import uuid
from app.schemas.anomaly import AnomalyResult
from app.models.alert import Alert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def detect_anomalies(
    db: AsyncSession,
    district_id: str,
    historical_daily_counts: List[Tuple[datetime, int]]
) -> List[AnomalyResult]:
    """
    Detects anomalies (e.g. crime spikes) using historical daily counts.
    Saves new anomalies to the Postgres 'alerts' table to act as the single source for Alerts.
    """
    anomalies = []
    
    if len(historical_daily_counts) < 7:
        return anomalies # Not enough data to baseline
        
    counts = [c for _, c in historical_daily_counts]
    dates = [d for d, _ in historical_daily_counts]
    
    # Calculate baseline over the first N-1 days
    baseline_counts = counts[:-1]
    current_count = counts[-1]
    current_date = dates[-1]
    
    mean = sum(baseline_counts) / len(baseline_counts)
    variance = sum((x - mean) ** 2 for x in baseline_counts) / max(len(baseline_counts), 1)
    std_dev = math.sqrt(variance)
    
    # Deviation check: 2 standard deviations
    threshold = mean + (2 * std_dev)
    
    if current_count > threshold and current_count > 0:
        severity = "HIGH" if current_count > mean + (3 * std_dev) else "MEDIUM"
        
        anomaly = AnomalyResult(
            id=str(uuid.uuid4()),
            anomaly_type="CRIME_SPIKE",
            severity=severity,
            affected_scope=f"DISTRICT:{district_id}" if district_id else "STATEWIDE",
            description=f"Unusual crime spike detected. Count {current_count} exceeds baseline mean {round(mean, 1)}.",
            detection_timestamp=datetime.now(timezone.utc),
            related_entity_id=district_id or "ALL"
        )
        anomalies.append(anomaly)
        
    # Check if this anomaly already triggered an alert for this date/district
    if anomalies:
        for anomaly in anomalies:
            # Simple deduplication strategy: check if an active anomaly alert exists for this district today
            query = select(Alert).where(
                Alert.type == "ANOMALY",
                Alert.district_id == district_id,
                Alert.status == "active"
            )
            result = await db.execute(query)
            existing = result.scalars().first()
            
            if not existing:
                # Insert new Alert to feed Phase 3D's /alerts endpoints directly
                new_alert = Alert(
                    id=anomaly.id,
                    type="ANOMALY",
                    severity=anomaly.severity,
                    status="active",
                    message=anomaly.description,
                    district_id=district_id
                )
                db.add(new_alert)
                await db.commit()
                
    return anomalies
