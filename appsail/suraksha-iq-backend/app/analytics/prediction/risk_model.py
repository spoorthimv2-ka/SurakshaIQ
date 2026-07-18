from app.schemas.offender import OffenderSummary
from app.schemas.risk import RiskScoreResponse

def calculate_offender_risk(offender: OffenderSummary) -> RiskScoreResponse:
    """
    Calculates a risk score (0-100) based on offender history retrieved from Neo4j.
    """
    count = offender.offense_count
    
    # Base weight: 20 points per offense, max 80 from count alone
    base_score = min(count * 20.0, 80.0)
    
    factors = []
    factors.append(f"Historical offense count: {count}")
    
    # Bonus for high frequency
    if count >= 5:
        base_score += 15
        factors.append("Chronic repeat offender status (5+ linked cases)")
    elif count >= 3:
        base_score += 10
        factors.append("Multiple repeat offenses (3+ linked cases)")
        
    final_score = min(base_score, 100.0)
    
    # Classify
    if final_score >= 70:
        classification = "HIGH"
    elif final_score >= 40:
        classification = "MEDIUM"
    else:
        classification = "LOW"
        
    return RiskScoreResponse(
        entity_id=offender.offender_id,
        entity_type="OFFENDER",
        risk_score=round(final_score, 1),
        risk_classification=classification,
        contributing_factors=factors
    )
