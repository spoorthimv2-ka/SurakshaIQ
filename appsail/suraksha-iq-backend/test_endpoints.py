import requests
import json
import sys

BASE = "http://localhost:8000"
ENDPOINTS = [
    "/api/v1/dashboard/summary",
    "/api/v1/dashboard/recent-crimes",
    "/api/v1/dashboard/recent-firs",
    "/api/v1/dashboard/crime-trends",
    "/api/v1/dashboard/district-summary",
    "/api/v1/hotspots/",
    "/api/v1/hotspots/top",
    "/api/v1/hotspots/stations",
    "/api/v1/hotspots/districts",
    "/api/v1/network/",
    "/api/v1/repeat-offenders/",
    "/api/v1/repeat-offenders/top",
    "/api/v1/repeat-offenders/statistics",
    "/api/v1/risk/",
    "/api/v1/risk/summary",
    "/api/v1/risk/districts",
    "/api/v1/risk/stations",
    "/api/v1/anomaly/",
    "/api/v1/anomaly/summary",
    "/api/v1/anomaly/districts",
    "/api/v1/anomaly/stations",
    "/api/v1/alerts/",
    "/api/v1/alerts/summary",
    "/api/v1/alerts/active",
    "/api/v1/reports/",
    "/api/v1/reports/summary",
    "/api/v1/reports/types",
    "/api/v1/firs/",
    "/api/v1/crimes/",
    "/api/v1/search/?keyword=a",
    "/api/v1/search/suggestions?keyword=test",
    "/api/v1/search/filters",
]

results = []
for ep in ENDPOINTS:
    url = BASE + ep
    try:
        r = requests.get(url, timeout=10)
        status = r.status_code
        body = r.text[:200] if r.text else ""
        ok = (status == 200)
        results.append((url, status, ok, body))
    except Exception as e:
        results.append((url, 0, False, str(e)))

failures = [(u, s, b) for u, s, ok, b in results if not ok]
print("=== ENDPOINT RESULTS ===")
for u, s, ok, b in results:
    status_str = "OK" if ok else "FAIL"
    print(f"[{status_str}] {u} -> {s}")
    if not ok:
        print(f"       Body: {b}")

print(f"\n=== SUMMARY ===")
print(f"Total: {len(results)}")
print(f"OK: {len(results) - len(failures)}")
print(f"FAIL: {len(failures)}")

if failures:
    print("\n=== FAILURES ===")
    for u, s, b in failures:
        print(f"  {u}: {s} - {b}")
    sys.exit(1)
else:
    print("\nAll endpoints returned 200 or allowed 4xx.")
    sys.exit(0)
