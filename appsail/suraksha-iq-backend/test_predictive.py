import os
os.environ.setdefault("MOCK_CATALYST_DATA", "true")
os.environ.setdefault("DEV_SKIP_AUTH", "true")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DEBUG", "true")

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test predictive endpoints
print("=== Testing Predictive Intelligence ===")

endpoints = [
    "/api/v1/predictive/forecast?time_period=30d",
    "/api/v1/predictive/emerging-hotspots",
    "/api/v1/predictive/risk-index",
    "/api/v1/predictive/patrol-recommendations",
    "/api/v1/predictive/temporal-intelligence",
    "/api/v1/predictive/trend-analysis",
    "/api/v1/predictive/dashboard",
]

for path in endpoints:
    try:
        r = client.get(path)
        print(f"{path}: {r.status_code}")
        if r.status_code != 200:
            print(f"  Body: {r.text[:500]}")
    except Exception as e:
        print(f"{path}: EXCEPTION {type(e).__name__}: {e}")

# Test scenario simulator
print("\n=== Testing Scenario Simulator ===")
try:
    r = client.post("/api/v1/predictive/scenario-simulator", json={"time_window": "30d"})
    print(f"POST /api/v1/predictive/scenario-simulator: {r.status_code}")
    if r.status_code != 200:
        print(f"  Body: {r.text[:500]}")
except Exception as e:
    print(f"POST /api/v1/predictive/scenario-simulator: EXCEPTION {type(e).__name__}: {e}")

# Test AI intelligence
print("\n=== Testing AI Intelligence ===")
try:
    r = client.post("/api/v1/predictive/ai-intelligence", json={"filters": {"time_period": "30d"}})
    print(f"POST /api/v1/predictive/ai-intelligence: {r.status_code}")
    if r.status_code != 200:
        print(f"  Body: {r.text[:500]}")
except Exception as e:
    print(f"POST /api/v1/predictive/ai-intelligence: EXCEPTION {type(e).__name__}: {e}")
