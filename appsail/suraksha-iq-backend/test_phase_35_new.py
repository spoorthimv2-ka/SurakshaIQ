import os
os.environ.setdefault("MOCK_CATALYST_DATA", "true")
os.environ.setdefault("DEV_SKIP_AUTH", "true")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DEBUG", "true")

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("=== Testing Settings & Notifications ===")
endpoints = [
    "/api/v1/settings/user",
    "/api/v1/settings/system",
    "/api/v1/settings/notifications",
    "/api/v1/settings/notifications/summary",
]
for path in endpoints:
    try:
        r = client.get(path)
        print(f"GET {path}: {r.status_code}")
        if r.status_code != 200:
            print(f"  Body: {r.text[:500]}")
    except Exception as e:
        print(f"GET {path}: EXCEPTION {type(e).__name__}: {e}")

print("\n=== Testing Admin New Endpoints ===")
admin_endpoints = [
    "/api/v1/admin/officers",
    "/api/v1/admin/districts",
    "/api/v1/admin/police-stations",
]
for path in admin_endpoints:
    try:
        r = client.get(path)
        print(f"GET {path}: {r.status_code}")
        if r.status_code != 200:
            print(f"  Body: {r.text[:500]}")
    except Exception as e:
        print(f"GET {path}: EXCEPTION {type(e).__name__}: {e}")
