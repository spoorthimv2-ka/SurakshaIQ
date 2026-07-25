"""
Tests for Phase 2.2 Operational AI Intelligence.

Covers:
- Executive summary
- FIR intelligence
- Crime pattern discovery
- Recommendations engine
- AI report generation
- Chat assistant
- Explain endpoint
- Evidence summary
- Timeline generation
- Persistent fallback behavior
"""

import os
import pytest
from unittest.mock import patch

os.environ.setdefault("MOCK_CATALYST_DATA", "true")
os.environ.setdefault("DEV_SKIP_AUTH", "true")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DEBUG", "true")


@pytest.fixture(autouse=True)
def _force_offline_ai():
    with (
        patch(
            "app.services.ai.catalyst_ai_client.CatalystAIClient.is_configured",
            return_value=False,
        )
    ):
        yield


@pytest.fixture
def dashboard_payload():
    return {
        "kpi_metrics": {
            "total_crimes": 120,
            "active_firs": 85,
            "closed_firs": 35,
            "detection_rate": 62.5,
            "hotspot_count": 4,
        },
        "crime_trends": [
            {"period": "2024-01", "count": 20},
            {"period": "2024-02", "count": 25},
            {"period": "2024-03", "count": 30},
        ],
        "hotspots": [
            {"location": "Bangalore", "riskLevel": "High", "severity": "HIGH", "district_id": "D1", "station_id": "S1"},
            {"location": "Mysore", "riskLevel": "Medium", "severity": "MEDIUM", "district_id": "D2", "station_id": "S2"},
        ],
        "district_statistics": [
            {"district_id": "D1", "district_name": "Bangalore", "crime_count": 80, "fir_count": 60, "active_investigations": 45},
            {"district_id": "D2", "district_name": "Mysore", "crime_count": 40, "fir_count": 25, "active_investigations": 20},
        ],
        "alerts": [
            {"alert_id": "ALT-01", "severity": "High", "title": "Rising theft spree"},
            {"alert_id": "ALT-02", "severity": "Low", "title": "Suspicious vehicle sighting"},
        ],
        "risk_scores": [
            {"district_id": "D1", "score": 0.82},
            {"district_id": "D2", "score": 0.45},
        ],
        "network_summary": {"total_networks": 12, "connected_offenders": 34},
        "repeat_offender_stats": {"top_offenders": [{"name": "X", "offences": 7}]},
    }


def test_executive_summary_fallback(client, dashboard_payload):
    response = client.post(
        "/api/v1/ai/summary",
        json={
            "filters": {"district_id": "D1"},
            "dashboard_payload": dashboard_payload,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["overallRisk"] == "High"
    assert body["isFallback"] is True
    assert 0.0 <= body["confidence"] <= 1.0
    assert body["generatedAt"]
    assert body["analyticsUsed"]


def test_chat_hotspot_query(client, dashboard_payload):
    response = client.post(
        "/api/v1/ai/chat",
        json={
            "message": "What hotspots are currently active?",
            "context": {"analytics": dashboard_payload},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "response" in body
    assert body["confidence"] >= 0.0
    assert body["isFallback"] is True
    assert "hotspots" in body["analyticsUsed"]


def test_chat_outside_scope(client):
    response = client.post(
        "/api/v1/ai/chat",
        json={
            "message": "Tell me about the weather in Bangalore.",
            "context": {},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "response" in body
    assert body["isFallback"] is True


def test_fir_intelligence(client):
    fir_payload = {
        "fir_number": "FIR-2024-001",
        "description": "A theft occurred at a shop on MG Road, Bangalore. Suspect was seen in a white KA51AB1234.",
        "sections": "IPC 380",
        "victim_name": "Ramesh",
        "suspect_name": "Unknown",
        "district_id": "D1",
        "station_id": "S1",
        "status": "ACTIVE",
    }
    response = client.post(
        "/api/v1/ai/fir-intelligence",
        json=fir_payload,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["crime_category"] == "theft"
    assert body["severity"] in {"Low", "Medium", "High", "Critical"}
    assert body["modus_operandi"]
    assert body["generatedAt"]
    assert body["isFallback"] is True
    assert body["confidence"] >= 0.0


def test_pattern_discovery(client, dashboard_payload):
    response = client.post(
        "/api/v1/ai/patterns",
        json={"analytics": dashboard_payload},
    )
    assert response.status_code == 200
    body = response.json()
    assert "patterns" in body
    assert "correlations" in body
    assert body["generatedAt"]
    assert body["isFallback"] is True
    assert 0.0 <= body["confidence"] <= 1.0


def test_recommendations(client, dashboard_payload):
    response = client.post(
        "/api/v1/ai/recommendations",
        json={"analytics": dashboard_payload},
    )
    assert response.status_code == 200
    body = response.json()
    assert "recommendations" in body
    assert "overall_risk" in body
    assert body["generatedAt"]
    assert body["isFallback"] is True
    assert 0.0 <= body["confidence"] <= 1.0
    for rec in body["recommendations"]:
        assert "title" in rec
        assert "priority" in rec
        assert "category" in rec


def test_intelligence_report(client):
    response = client.post(
        "/api/v1/ai/report",
        json={"report_type": "SITUATIONAL", "scope": {"district_id": "D1"}, "analytics": {
            "kpi_metrics": {"total_crimes": 120, "active_firs": 85},
            "hotspots": [{"district": "Bangalore", "severity": "HIGH"}],
        }},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["reportId"]
    assert body["title"]
    assert body["content"]
    assert body["format"] == "text"
    assert body["generatedAt"]
    assert body["isFallback"] is True
    assert 0.0 <= body["confidence"] <= 1.0


def test_explain_hotspot_map(client, dashboard_payload):
    response = client.post(
        "/api/v1/ai/explain",
        json={
            "chart_type": "hotspot_map",
            "data": dashboard_payload,
            "filters": {"district_id": "D1"},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["explanation"]
    assert body["confidence"] >= 0.0
    assert body["generatedAt"]
    assert body["isFallback"] is True


def test_explain_unknown_chart(client):
    response = client.post(
        "/api/v1/ai/explain",
        json={"chart_type": "unknown_scatter_plot", "data": {}, "filters": {}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["explanation"]


def test_evidence_summary(client):
    response = client.post(
        "/api/v1/ai/evidence-summary",
        json={
            "document_type": "WITNESS_STATEMENT",
            "content": "Witness saw a white KA51AB1234 fleeing the scene near MG Road at 9:45 pm.",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["summary"]
    assert "extracted_entities" in body
    assert body["confidence"] >= 0.0
    assert body["generatedAt"]
    assert body["isFallback"] is True


def test_timeline_generator(client):
    response = client.post(
        "/api/v1/ai/timeline",
        json={
            "incident_description": (
                "On 2024-01-15 around 9:45 pm, the victim was at MG Road. "
                "A suspect in a white car approached and threatened the victim. "
                "Later on 2024-01-16, the victim filed a complaint."
            ),
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "events" in body
    assert "narrative" in body
    assert len(body["events"]) >= 1
    assert body["confidence"] >= 0.0
    assert body["generatedAt"]
    assert body["isFallback"] is True


def test_cached_summary_returns_same(client, dashboard_payload):
    payload = {
        "filters": {"station_id": "S99"},
        "intelligence_scope": {"officer_id": "OFF-1"},
        "dashboard_payload": dashboard_payload,
    }
    r1 = client.post("/api/v1/ai/summary", json=payload)
    r2 = client.post("/api/v1/ai/summary", json=payload)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["overallRisk"] == r2.json()["overallRisk"]
