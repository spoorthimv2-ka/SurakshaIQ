import os
os.environ.setdefault("MOCK_CATALYST_DATA", "true")
os.environ.setdefault("DEV_SKIP_AUTH", "true")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DEBUG", "true")

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test repeat offenders endpoints
print("=== Testing Repeat Offenders ===")

for path in ["/api/v1/repeat-offenders/", "/api/v1/repeat-offenders/statistics", "/api/v1/repeat-offenders/top"]:
    try:
        r = client.get(path)
        print(f"{path}: {r.status_code}")
        if r.status_code != 200:
            print(f"  Body: {r.text[:500]}")
    except Exception as e:
        print(f"{path}: EXCEPTION {type(e).__name__}: {e}")

# Test network endpoints
print("\n=== Testing Network APIs ===")
for path in ["/api/v1/network/advanced", "/api/v1/network/analytics", "/api/v1/network/timeline"]:
    try:
        r = client.get(path)
        print(f"{path}: {r.status_code}")
        if r.status_code != 200:
            print(f"  Body: {r.text[:500]}")
    except Exception as e:
        print(f"{path}: EXCEPTION {type(e).__name__}: {e}")
