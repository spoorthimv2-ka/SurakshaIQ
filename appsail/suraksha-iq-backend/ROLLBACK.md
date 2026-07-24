# Rollback Plan — Data-Layer Stabilization (Catalyst-only)

## 1. Parameterized ZCQL Query Migration

| Change | Rollback |
|---|---|
| Replaced f-string value interpolation with `_zcql_escape()` in 16 repository files | `git checkout -- app/repositories/*.py` — restores original string-concatenated queries. Response shapes are identical, so no downstream rollback is needed. |
| Added `_validate_column()` allowlist to `base_repository.py` | Remove `_validate_column()` calls from query methods. Or `git checkout app/repositories/base_repository.py`. |
| Added `ALLOWED_COLUMNS` map to `base_repository.py` | Remove the map and `_validate_column()` calls. No data loss because this is runtime validation only. |

**Impact:** Low. No schema change, no data loss. Only query construction changes.

---

## 2. `CrimeCriminalLink` Catalyst Table

| Change | Rollback |
|---|---|
| Created Catalyst table `CrimeCriminalLink` (new rows only) | Delete the table via Catalyst console. Zero data loss. |
| Added `CrimeCriminalLinkRepository` and `CrimeCriminalLinkResponse` schema | Delete `app/repositories/crime_criminal_link_repo.py`, `app/schemas/crime_criminal_link.py`, `app/api/v1/crime_criminal_links/routes.py`, `app/api/v1/crime_criminal_links/__init__.py`. Unmount router from `router.py`. |
| Changed `RepeatOffenderService` to read explicit links by default | Revert to old district-proximity heuristic branch. No database effect. |
| Added `?include_heuristic=true` to repeat-offender routes | Remove the query param from the three affected routes. Frontend stops sending it; backend stops accepting it. |

**Impact:** Low. Table starts empty; explicit linkage is additive.

---

## 3. `CrimeHotspotCluster` Catalyst Table

| Change | Rollback |
|---|---|
| Created Catalyst table `CrimeHotspotCluster` | Delete the table via Catalyst console. Zero data loss. |
| Added `HotspotEngine` (`app/analytics/hotspot_engine.py`) | Delete the file. Existing hotspot endpoints continue to compute in-memory as before. |
| Added `app/analytics/spatial.py` (DBSCAN + haversine) | Delete the file. No other code depends on it yet. |

**Impact:** Low. Clustering is a cache layer; existing endpoints fall back to on-the-fly computation.

---

## 4. `PredictionLedger` Catalyst Table

| Change | Rollback |
|---|---|
| Created Catalyst table `PredictionLedger` | Delete the table via Catalyst console. Zero data loss. |
| Added `PredictionLedgerRepository` | Delete `app/repositories/prediction_ledger_repo.py`. |
| Added `_record_ledger()` write calls in 5 services | Remove the `_record_ledger` helper and the `await self._record_ledger(...)` lines from `hotspot_service.py`, `network_service.py`, `predictive_risk_service.py`, `anomaly_service.py`, and `repeat_offender_service.py`. Same response shapes; history simply stops appending. |
| Ledger writes are wrapped in `try/except` | Even if the table is deleted, the services continue to return predictions; ledger failures are logged as warnings, not raised. |

**Impact:** Low. Ledger writes are non-blocking side effects.

---

## 5. API Contract Document

| Change | Rollback |
|---|---|
| Added `API_CONTRACT.md` | Delete the file. No runtime effect. |

**Impact:** None.

---

## Fast Rollback Commands

```bash
# Revert all repository and service changes
git checkout -- app/repositories/ app/services/ app/api/

# Remove new files
rm -rf app/repositories/crime_criminal_link_repo.py
rm -rf app/repositories/prediction_ledger_repo.py
rm -rf app/schemas/crime_criminal_link.py
rm -rf app/api/v1/crime_criminal_links/
rm -rf app/analytics/spatial.py
rm -rf app/analytics/hotspot_engine.py
rm API_CONTRACT.md

# Re-import deleted dead-code files if needed (git restore)
git restore app/repositories/dashboard_repo.py
git restore app/repositories/officer_sql_repo.py
git restore app/analytics/anomaly/detector.py
git restore app/analytics/hotspot/clustering.py
```

**Demo-day guidance:** The fastest rollback is `git stash` or `git revert <commit>` because every change is additive or confined to query construction. No Catalyst table deletion is required if the code still references a deleted table — the repositories will raise `RepositoryError`, which maps to HTTP 503, giving you time to restore the table or code without corrupting existing data.
