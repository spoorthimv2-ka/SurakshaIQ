"""
Runtime audit script for SurakshaIQ backend.

Executes all known failing endpoints under local MockApp and captures:
  - HTTP status
  - Response body
  - Python traceback for unhandled exceptions
  - AI configuration details
  - Mock datastore queries
"""
import os
import sys
import json
import traceback
from datetime import datetime, timezone

# Force offline / mock mode before any app imports
os.environ.setdefault("MOCK_CATALYST_DATA", "true")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("DEV_SKIP_AUTH", "true")

# Add backend directory to path for app imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Monkey-patch MockZCQL to log queries and responses
# ---------------------------------------------------------------------------
from app.core import mock_data as _mock_data_mod

_original_mock_execute = _mock_data_mod.MockZCQL.execute_query

def _logging_execute(self, query: str):
    print(f"\n[ZCQL] {query}")
    try:
        result = _original_mock_execute(self, query)
        print(f"[ZCQL-RESULT] {json.dumps(result, default=str)[:2000]}")
        return result
    except Exception as exc:
        print(f"[ZCQL-ERROR] {exc}")
        raise

_mock_data_mod.MockZCQL.execute_query = _logging_execute

# ---------------------------------------------------------------------------
# Build a valid SYSTEM_ADMINISTRATOR JWT
# ---------------------------------------------------------------------------
from app.config.settings import settings as _settings
from app.security.jwt import create_access_token
from app.models.enums import Permission, Role

print("=" * 80)
print("AI / AUTH CONFIGURATION")
print("=" * 80)
print(f"CATALYST_PROJECT_ID : {_settings.catalyst_project_id!r}")
print(f"CATALYST_APP_KEY    : {_settings.catalyst_app_key!r}")
print(f"AI_API_KEY          : {_settings.ai_api_key!r}")
print(f"AI_BASE_URL         : {_settings.ai_base_url!r}")
print(f"AI_PROVIDER         : {_settings.ai_provider!r}")
print(f"AI_MODEL            : {_settings.ai_model!r}")
print(f"AI_FALLBACK_ENABLED : {_settings.ai_fallback_enabled!r}")
print(f"CatalystAIClient.is_configured() : {_settings.catalyst_project_id or _settings.ai_api_key or _settings.ai_base_url}")

payload = {
    "sub": "OFF-001",
    "cat_id": "USR-001",
    "badge_number": "KSP-000001",
    "role": Role.SYSTEM_ADMINISTRATOR.value,
    "permissions": [p.value for p in Permission],
    "jurisdiction_type": "STATION",
    "station_id": "STN-CENTRAL",
    "district_id": "DIST-CENTRAL",
    "state_access": True,
    "token_version": 1,
}
token = create_access_token(payload)
headers = {"Authorization": f"Bearer {token}"}

# ---------------------------------------------------------------------------
# Import app and client
# ---------------------------------------------------------------------------
from fastapi.testclient import TestClient
from main import app
from app.authorization.service import get_current_officer as _real_get_current_officer

MOCK_OFFICER = {
    "ROWID": "OFF-001",
    "user_id": "USR-001",
    "name": "Test Officer",
    "email": "test@suraksha.gov.in",
    "role": "SYSTEM_ADMINISTRATOR",
    "badge_number": "KSP-000001",
    "station_id": "STN-CENTRAL",
    "district_id": "DIST-CENTRAL",
    "permissions": [p.value for p in Permission],
    "token_version": 1,
    "state_access": True,
}

async def _mock_get_current_officer():
    return MOCK_OFFICER

app.dependency_overrides[_real_get_current_officer] = _mock_get_current_officer

client = TestClient(app)


def call(name, method, path, **kwargs):
    print("\n" + "=" * 80)
    print(f"[{name}] {method} {path}")
    print("=" * 80)
    try:
        if method.upper() == "GET":
            resp = client.get(path, headers=headers, **kwargs)
        elif method.upper() == "POST":
            resp = client.post(path, headers=headers, **kwargs)
        elif method.upper() == "DELETE":
            resp = client.delete(path, headers=headers, **kwargs)
        elif method.upper() == "PATCH":
            resp = client.patch(path, headers=headers, **kwargs)
        else:
            raise ValueError(f"Unsupported method {method}")
        print(f"STATUS: {resp.status_code}")
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        print(f"BODY: {json.dumps(body, default=str)[:3000]}")
    except Exception as exc:
        print(f"\n*** TRACEBACK for {name} ***")
        traceback.print_exc()
        print("=" * 80)


# ---------------------------------------------------------------------------
# AI ENDPOINTS
# ---------------------------------------------------------------------------
call("AI_SUMMARY", "POST", "/api/v1/ai/summary", json={
    "filters": {"district_id": "DIST-CENTRAL"},
    "dashboard_payload": {
        "kpi_metrics": {"total_crimes": 120, "active_firs": 85},
        "hotspots": [{"district": "Bangalore", "severity": "HIGH"}],
    },
})
call("AI_CHAT", "POST", "/api/v1/ai/chat", json={
    "message": "What hotspots are currently active?",
    "context": {"analytics": {"hotspots": [{"location": "B", "severity": "HIGH"}]}},
})
call("AI_FIR_INTEL", "POST", "/api/v1/ai/fir-intelligence", json={
    "fir_number": "FIR-2024-001",
    "description": "Theft near MG Road Bangalore KA51AB1234",
    "sections": "IPC 380",
    "district_id": "DIST-CENTRAL",
    "station_id": "STN-CENTRAL",
    "status": "ACTIVE",
})
call("AI_PATTERNS", "POST", "/api/v1/ai/patterns", json={
    "analytics": {"hotspots": [{"district": "Bangalore", "severity": "HIGH"}]},
})
call("AI_RECOMMENDATIONS", "POST", "/api/v1/ai/recommendations", json={
    "analytics": {"hotspots": [{"district": "Bangalore", "severity": "HIGH"}]},
})
call("AI_REPORT", "POST", "/api/v1/ai/report", json={
    "report_type": "SITUATIONAL",
    "scope": {"district_id": "DIST-CENTRAL"},
    "analytics": {"kpi_metrics": {"total_crimes": 120}},
})
call("AI_EXPLAIN", "POST", "/api/v1/ai/explain", json={
    "chart_type": "hotspot_map",
    "data": {"hotspots": [{"location": "B", "severity": "HIGH"}]},
    "filters": {"district_id": "DIST-CENTRAL"},
})
call("AI_EVIDENCE", "POST", "/api/v1/ai/evidence-summary", json={
    "document_type": "WITNESS_STATEMENT",
    "content": "Witness saw a white KA51AB1234 fleeing near MG Road at 9:45 pm.",
})
call("AI_TIMELINE", "POST", "/api/v1/ai/timeline", json={
    "incident_description": "On 2024-01-15 around 9:45 pm, theft at MG Road."
})

# ---------------------------------------------------------------------------
# HOTSPOTS
# ---------------------------------------------------------------------------
call("HOTSPOTS", "GET", "/api/v1/hotspots/")
call("DISTRICT_HOTSPOTS", "GET", "/api/v1/hotspots/districts")
call("STATION_HOTSPOTS", "GET", "/api/v1/hotspots/stations")
call("TOP_HOTSPOTS", "GET", "/api/v1/hotspots/top")

# ---------------------------------------------------------------------------
# PREDICTIVE
# ---------------------------------------------------------------------------
call("FORECAST", "GET", "/api/v1/predictive/forecast?time_period=30d")
call("EMERGING_HOTSPOTS", "GET", "/api/v1/predictive/emerging-hotspots")
call("RISK_INDEX", "GET", "/api/v1/predictive/risk-index")
call("PATROL_RECS", "GET", "/api/v1/predictive/patrol-recommendations")
call("TEMPORAL", "GET", "/api/v1/predictive/temporal-intelligence")
call("TREND_ANALYSIS", "GET", "/api/v1/predictive/trend-analysis")
call("PREDICTIVE_DASHBOARD", "GET", "/api/v1/predictive/dashboard")

# ---------------------------------------------------------------------------
# PREDICTIVE RISK
# ---------------------------------------------------------------------------
call("RISK_PREDICTIONS", "GET", "/api/v1/predictive-risk/")
call("RISK_SUMMARY", "GET", "/api/v1/predictive-risk/summary")
call("DISTRICT_RISK", "GET", "/api/v1/predictive-risk/districts")
call("STATION_RISK", "GET", "/api/v1/predictive-risk/stations")

# ---------------------------------------------------------------------------
# NETWORK
# ---------------------------------------------------------------------------
call("NETWORK", "GET", "/api/v1/network/")
call("NETWORK_STATS", "GET", "/api/v1/network/statistics")
call("NETWORK_ANALYTICS", "GET", "/api/v1/network/analytics")
call("NETWORK_COMMUNITIES", "GET", "/api/v1/network/communities")
call("NETWORK_CENTRAL", "GET", "/api/v1/network/central-actors")
call("NETWORK_BRIDGES", "GET", "/api/v1/network/bridge-nodes")
call("NETWORK_SEARCH", "GET", "/api/v1/network/search?q=Bangalore")

# ---------------------------------------------------------------------------
# REPEAT OFFENDERS
# ---------------------------------------------------------------------------
call("REPEAT_OFFENDERS", "GET", "/api/v1/repeat-offenders/")
call("TOP_OFFENDERS", "GET", "/api/v1/repeat-offenders/top")
call("OFFENDER_STATS", "GET", "/api/v1/repeat-offenders/statistics")

# ---------------------------------------------------------------------------
# REPORTS
# ---------------------------------------------------------------------------
call("REPORTS", "GET", "/api/v1/reports/")
call("REPORT_SUMMARY", "GET", "/api/v1/reports/summary")
call("REPORT_TYPES", "GET", "/api/v1/reports/types")

# ---------------------------------------------------------------------------
# ADMIN
# ---------------------------------------------------------------------------
call("ADMIN_USERS", "GET", "/api/v1/admin/users")
call("ADMIN_STATS", "GET", "/api/v1/admin/statistics")
call("ADMIN_ROLES", "GET", "/api/v1/admin/roles")
call("ADMIN_OFFICERS", "GET", "/api/v1/admin/officers")
call("ADMIN_DISTRICTS", "GET", "/api/v1/admin/districts")
call("ADMIN_STATIONS", "GET", "/api/v1/admin/police-stations")
call("ADMIN_LOGS", "GET", "/api/v1/admin/audit-logs")

print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
