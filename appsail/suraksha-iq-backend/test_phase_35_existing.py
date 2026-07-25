import os
os.environ.setdefault("MOCK_CATALYST_DATA", "true")
os.environ.setdefault("DEV_SKIP_AUTH", "true")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DEBUG", "true")

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test admin endpoints
print("=== Testing Admin Endpoints ===")
admin_endpoints = [
    "/api/v1/admin/users",
    "/api/v1/admin/roles",
    "/api/v1/admin/statistics",
    "/api/v1/admin/audit-logs",
]
for path in admin_endpoints:
    try:
        r = client.get(path)
        print(f"GET {path}: {r.status_code}")
        if r.status_code != 200:
            print(f"  Body: {r.text[:300]}")
    except Exception as e:
        print(f"GET {path}: EXCEPTION {type(e).__name__}: {e}")

# Test reports endpoints
print("\n=== Testing Reports Endpoints ===")
report_endpoints = [
    "/api/v1/reports/",
    "/api/v1/reports/summary",
    "/api/v1/reports/types",
]
for path in report_endpoints:
    try:
        r = client.get(path)
        print(f"GET {path}: {r.status_code}")
        if r.status_code != 200:
            print(f"  Body: {r.text[:300]}")
    except Exception as e:
        print(f"GET {path}: EXCEPTION {type(e).__name__}: {e}")

# Test districts endpoints
print("\n=== Testing Districts Endpoints ===")
district_endpoints = [
    "/api/v1/districts/",
]
for path in district_endpoints:
    try:
        r = client.get(path)
        print(f"GET {path}: {r.status_code}")
        if r.status_code != 200:
            print(f"  Body: {r.text[:300]}")
    except Exception as e:
        print(f"GET {path}: EXCEPTION {type(e).__name__}: {e}")
