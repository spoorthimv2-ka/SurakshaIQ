# Catalyst Datastore Schema for SurakshaIQ Backend

Generated from actual source code inspection of:
- `appsail/suraksha-iq-backend/app/models/`
- `appsail/suraksha-iq-backend/app/schemas/`
- `appsail/suraksha-iq-backend/app/repositories/`
- `appsail/suraksha-iq-backend/app/services/`
- `functions/system_setup/catalyst_bootstrap/datastore_bootstrap.py`

---

# Table: District

**Purpose:** Geographic administrative unit (state/district). Root of jurisdiction hierarchy.

| Column | Data Type | Max Length | Mandatory | Unique | Default | Indexed/Searchable |
|--------|-----------|------------|-----------|--------|---------|-------------------|
| name | varchar | 100 | Yes | Yes | — | Indexed |
| state | varchar | 100 | Yes | No | — | — |
| region_code | varchar | 50 | No | No | — | — |
| latitude | decimal | — | No | No | — | — |
| longitude | decimal | — | No | No | — | — |
| status | varchar | 20 | No | No | ACTIVE | — |
| code | varchar | 50 | Yes | Yes | — | Indexed |

- **Primary lookup key:** `code`
- **Frequently queried columns:** `name`, `code`, `status`
- **Foreign-key relationships (logical):** Referenced by `PoliceStation.district_id`, `Crime.district_id`, `FIR.district_id`, `Alert.district_id`, `CrimeHotspotCluster.district_id`, `Anomaly.district_id`, `PredictiveRisk.district_id`
- **Used by:** `DistrictRepository`, `DistrictService`, ` CrimeService`, `FIRService`, `AlertService`, `ReportService`, `NetworkRepository`, `AnomalyRepository`, `PredictiveRiskRepository`, `HotspotService`, `AdminRepository`, `SearchRepository`

---

# Table: PoliceStation

**Purpose:** Individual police station unit scoped to a district.

| Column | Data Type | Max Length | Mandatory | Unique | Default | Indexed/Searchable |
|--------|-----------|------------|-----------|--------|---------|-------------------|
| name | varchar | 150 | Yes | No | — | Indexed |
| station_code | varchar | 50 | Yes | Yes | — | Indexed |
| address | varchar | 255 | No | No | — | — |
| district_id | varchar | 50 | Yes | No | — | Indexed |
| latitude | decimal | — | No | No | — | — |
| longitude | decimal | — | No | No | — | — |
| status | varchar | 20 | No | No | ACTIVE | — |

- **Primary lookup key:** `station_code`
- **Frequently queried columns:** `district_id`, `station_code`, `status`, `name`
- **Foreign-key relationships (logical):** References `District` via `district_id`; referenced by `Officer.police_station_id`, `Crime.station_id`, `FIR.station_id`, `CrimeHotspotCluster.station_id`, `NetworkNode` edges
- **Used by:** `PoliceStationRepository`, `PoliceStationService`, `CrimeService`, `FIRService`, `AlertService`, `ReportService`, `NetworkRepository`, `HotspotService`, `AnomalyRepository`, `PredictiveRiskRepository`, `AdminRepository`, `SearchRepository`

---

# Table: Officer

**Purpose:** Authenticated law enforcement user profile for login, RBAC, and jurisdiction scoping.

| Column | Data Type | Max Length | Mandatory | Unique | Default | Indexed/Searchable |
|--------|-----------|------------|-----------|--------|---------|-------------------|
| catalyst_user_id | varchar | 100 | Yes | Yes | — | Indexed |
| name | varchar | 150 | Yes | No | — | — |
| email | varchar | 255 | Yes | Yes | — | Indexed |
| role | varchar | 50 | Yes | No | — | — |
| rank | varchar | 100 | No | No | — | — |
| designation | varchar | 100 | No | No | — | — |
| hashed_password | varchar | 255 | No | No | — | — |
| badge_number | varchar | 50 | Yes | Yes | — | Indexed |
| police_station_id | varchar | 50 | No | No | — | — |
| district_id | varchar | 50 | No | No | — | — |
| jurisdiction_type | varchar | 20 | No | No | STATION | — |
| account_status | varchar | 20 | No | No | ACTIVE | — |
| last_login | varchar | 50 | No | No | — | — |
| failed_attempts | int | — | No | No | 0 | — |
| locked_until | varchar | 50 | No | No | — | — |
| status | varchar | 20 | No | No | ACTIVE | — |

- **Primary lookup key:** `badge_number`
- **Frequently queried columns:** `badge_number`, `email`, `catalyst_user_id`, `status`, `police_station_id`, `district_id`
- **Foreign-key relationships (logical):** References `PoliceStation` via `police_station_id`; referenced by `Report.created_by_officer_id`, `FIR.officer_id`, `CrimeCriminalLink.linked_by_officer_id`
- **Used by:** `OfficerRepository`, `CatalystOfficerRepository`, `OfficerService`, `AuthService`, `AdminRepository`, `FIRService`, `ReportService`, `NetworkRepository`, `SearchRepository`, `AnomalyRepository`, `PredictiveRiskRepository`, `HotspotService`

---

# Table: Crime

**Purpose:** Primary case/incident record linked to an FIR and location.

| Column | Data Type | Max Length | Mandatory | Unique | Default | Indexed/Searchable |
|--------|-----------|------------|-----------|--------|---------|-------------------|
| fir_number | varchar | 100 | Yes | Yes | — | Indexed |
| crime_type | varchar | 100 | Yes | No | — | Indexed |
| description | text | — | No | No | — | Searchable |
| incident_date | datetime | — | Yes | No | — | Indexed |
| status | varchar | 20 | No | No | ACTIVE | Indexed |
| severity | varchar | 20 | No | No | — | — |
| latitude | decimal | — | No | No | — | — |
| longitude | decimal | — | No | No | — | — |
| address | varchar | 255 | No | No | — | — |
| district_id | varchar | 50 | Yes | No | — | Indexed |
| station_id | varchar | 50 | Yes | No | — | Indexed |
| title | varchar | 255 | Yes | No | — | Searchable |
| location | varchar | 100 | Yes | No | — | Searchable |
| victim_name | varchar | 100 | No | No | — | Searchable |
| suspect_name | varchar | 100 | No | No | — | Searchable |
| alias | varchar | 100 | No | No | — | Searchable |
| vehicle_number | varchar | 20 | No | No | — | Searchable |
| mobile_number | varchar | 20 | No | No | — | Searchable |
| weapon | varchar | 100 | No | No | — | Searchable |
| modus_operandi | varchar | 100 | No | No | — | Searchable |
| keywords | varchar | 100 | No | No | — | Searchable |
| ipc_sections | varchar | 100 | No | No | — | Searchable |

- **Primary lookup key:** `fir_number`
- **Frequently queried columns:** `district_id`, `station_id`, `status`, `crime_type`, `title`
- **Foreign-key relationships (logical):** References `District` via `district_id`; references `PoliceStation` via `station_id`; referenced by `FIR.crime_id`, `CrimeCriminalLink.crime_id`, `CrimeHotspotCluster`
- **Used by:** `CrimeRepository`, `CrimeService`, `FIRService`, `AlertService`, `ReportService`, `NetworkRepository`, `AnomalyRepository`, `PredictiveRiskRepository`, `HotspotRepository`, `DashboardService`, `SearchRepository`

---

# Table: FIR

**Purpose:** First Information Report formal record registered against a crime.

| Column | Data Type | Max Length | Mandatory | Unique | Default | Indexed/Searchable |
|--------|-----------|------------|-----------|--------|---------|-------------------|
| fir_number | varchar | 100 | Yes | Yes | — | Indexed |
| crime_id | varchar | 50 | Yes | No | — | Indexed |
| district_id | varchar | 50 | Yes | No | — | Indexed |
| station_id | varchar | 50 | Yes | No | — | Indexed |
| officer_id | varchar | 50 | Yes | No | — | Indexed |
| description | text | — | Yes | No | — | Searchable |
| sections | varchar | 100 | No | No | — | — |
| summary | text | — | No | No | — | — |
| fir_date | datetime | — | Yes | No | — | — |
| status | varchar | 20 | No | No | ACTIVE | — |
| victim_name | varchar | 100 | No | No | — | Searchable |
| suspect_name | varchar | 100 | No | No | — | Searchable |
| vehicle_number | varchar | 20 | No | No | — | Searchable |
| mobile_number | varchar | 20 | No | No | — | Searchable |
| ipc_sections | varchar | 100 | No | No | — | Searchable |

- **Primary lookup key:** `fir_number`
- **Frequently queried columns:** `fir_number`, `district_id`, `station_id`, `officer_id`, `status`, `crime_id`
- **Foreign-key relationships (logical):** References `Crime` via `crime_id`; references `District` via `district_id`; references `PoliceStation` via `station_id`; references `Officer` via `officer_id`
- **Used by:** `FIRRepository`, `FIRService`, `ReportService`, `NetworkRepository`, `AnomalyRepository`, `PredictiveRiskRepository`, `HotspotService`, `DashboardService`, `SearchRepository`

---

# Table: Criminal

**Purpose:** Known offender/criminal profile with risk classification.

| Column | Data Type | Max Length | Mandatory | Unique | Default | Indexed/Searchable |
|--------|-----------|------------|-----------|--------|---------|-------------------|
| name | varchar | 150 | Yes | No | — | Searchable |
| alias | varchar | 100 | No | No | — | Searchable |
| age | int | — | No | No | — | — |
| gender | varchar | 10 | No | No | — | — |
| last_known_location | varchar | 100 | No | No | — | — |
| risk_level | varchar | 20 | Yes | No | — | — |
| status | varchar | 20 | No | No | ACTIVE | — |
| photo_url | text | — | No | No | — | — |

- **Primary lookup key:** `ROWID`
- **Frequently queried columns:** `status`, `risk_level`, `last_known_location`, `name`, `alias`
- **Foreign-key relationships (logical):** Referenced by `CrimeCriminalLink.criminal_id`
- **Used by:** `CriminalRepository`, `CriminalService`, `NetworkRepository`, `AnomalyRepository`, `PredictiveRiskRepository`, `RepeatOffenderRepository`, `ReportService`, `SearchRepository`

---

# Table: Alert

**Purpose:** Operational alert generated from anomalies, hotspots, or system rules.

| Column | Data Type | Max Length | Mandatory | Unique | Default | Indexed/Searchable |
|--------|-----------|------------|-----------|--------|---------|-------------------|
| type | varchar | 50 | Yes | No | — | — |
| severity | varchar | 20 | Yes | No | — | — |
| status | varchar | 20 | No | No | ACTIVE | — |
| message | text | — | Yes | No | — | — |
| district_id | varchar | 50 | No | No | — | — |
| created_at | datetime | — | No | No | — | — |
| resolved_at | datetime | — | No | No | — | — |
| title | varchar | 255 | Yes | No | — | Searchable |
| description | text | — | Yes | No | — | Searchable |
| source | varchar | 50 | Yes | No | — | — |
| entity_id | varchar | 50 | No | No | — | — |
| entity_type | varchar | 50 | No | No | — | — |
| station_id | varchar | 50 | No | No | — | — |
| recommended_action | text | — | No | No | — | — |

- **Primary lookup key:** `ROWID`
- **Frequently queried columns:** `district_id`, `status`, `severity`, `type`, `station_id`
- **Foreign-key relationships (logical):** References `District` via `district_id`; references `PoliceStation` via `station_id`
- **Used by:** `AlertRepository`, `AlertService`, `ReportService`, `DashboardService`, `SearchRepository`

---

# Table: Report

**Purpose:** Generated operational or analytical report snapshot.

| Column | Data Type | Max Length | Mandatory | Unique | Default | Indexed/Searchable |
|--------|-----------|------------|-----------|--------|---------|-------------------|
| name | varchar | 255 | Yes | No | — | Searchable |
| report_type | varchar | 50 | Yes | No | — | Indexed |
| parameters_json | json | — | No | No | — | — |
| created_by_officer_id | varchar | 50 | Yes | No | — | — |
| created_at | datetime | — | No | No | — | — |

- **Primary lookup key:** `ROWID`
- **Frequently queried columns:** `report_type`, `created_by_officer_id`, `name`
- **Foreign-key relationships (logical):** References `Officer` via `created_by_officer_id`
- **Used by:** `ReportRepository`, `ReportService`

---

# Table: User

**Purpose:** Generic user profile separate from Officer; used for authentication identity and settings.

| Column | Data Type | Max Length | Mandatory | Unique | Default | Indexed/Searchable |
|--------|-----------|------------|-----------|--------|---------|-------------------|
| name | varchar | 150 | Yes | No | — | — |
| email | varchar | 255 | Yes | Yes | — | Indexed |
| role | varchar | 50 | Yes | No | — | — |
| status | varchar | 20 | No | No | ACTIVE | — |

- **Primary lookup key:** `email`
- **Frequently queried columns:** `email`, `role`, `status`, `name`
- **Foreign-key relationships (logical):** Linked to `Officer` via shared email / ROWID correlation in admin logic
- **Used by:** `UserRepository`, `UserService`, `AdminRepository`, `SettingsService`

---

# Table: CrimeCriminalLink

**Purpose:** Explicit many-to-many linkage between crimes and criminals with role metadata.

| Column | Data Type | Max Length | Mandatory | Unique | Default | Indexed/Searchable |
|--------|-----------|------------|-----------|--------|---------|-------------------|
| crime_id | varchar | 50 | Yes | No | — | Indexed |
| criminal_id | varchar | 50 | Yes | No | — | Indexed |
| role | varchar | 20 | No | No | ACCUSED | — |
| linked_by_officer_id | varchar | 50 | No | No | — | — |
| linked_at | datetime | — | No | No | — | — |
| notes | text | — | No | No | — | — |

- **Primary lookup key:** `ROWID`
- **Frequently queried columns:** `crime_id`, `criminal_id`
- **Foreign-key relationships (logical):** References `Crime` via `crime_id`; references `Criminal` via `criminal_id`; references `Officer` via `linked_by_officer_id`
- **Used by:** `CrimeCriminalLinkRepository`, `NetworkRepository`, `SearchRepository`

---

# Table: CrimeHotspotCluster

**Purpose:** Derived geospatial cluster of crimes for hotspot analysis.

| Column | Data Type | Max Length | Mandatory | Unique | Default | Indexed/Searchable |
|--------|-----------|------------|-----------|--------|---------|-------------------|
| cluster_id | varchar | 50 | Yes | Yes | — | Indexed |
| district_id | varchar | 50 | Yes | No | — | Indexed |
| station_id | varchar | 50 | Yes | No | — | Indexed |
| center_lat | decimal | — | Yes | No | — | — |
| center_lon | decimal | — | Yes | No | — | — |
| radius_m | int | — | Yes | No | — | — |
| crime_count | int | — | Yes | No | — | — |
| period_start | datetime | — | Yes | No | — | — |
| period_end | datetime | — | Yes | No | — | — |
| scored_at | datetime | — | Yes | No | — | — |

- **Primary lookup key:** `cluster_id`
- **Frequently queried columns:** `district_id`, `station_id`, `cluster_id`
- **Foreign-key relationships (logical):** References `District` via `district_id`; references `PoliceStation` via `station_id`
- **Used by:** `HotspotService`, `ReportService`, `SearchRepository`

---

# Table: PredictionLedger

**Purpose:** Immutable audit history of all predictive/risk/scoring run outputs.

| Column | Data Type | Max Length | Mandatory | Unique | Default | Indexed/Searchable |
|--------|-----------|------------|-----------|--------|---------|-------------------|
| entity_type | varchar | 50 | Yes | No | — | — |
| entity_id | varchar | 50 | Yes | No | — | — |
| entity_name | varchar | 100 | Yes | No | — | — |
| prediction_type | varchar | 50 | Yes | No | — | — |
| score | decimal | — | Yes | No | — | — |
| level | varchar | 20 | Yes | No | — | — |
| factors | json | — | No | No | — | — |
| model_version | varchar | 50 | Yes | No | — | — |
| scored_at | datetime | — | Yes | No | — | — |

- **Primary lookup key:** `ROWID`
- **Frequently queried columns:** `entity_type`, `entity_id`, `prediction_type`
- **Foreign-key relationships (logical):** Semantic references to `District`, `PoliceStation`, etc. via `entity_type` + `entity_id`
- **Used by:** `PredictionLedgerRepository`, `HotspotService`, `AnomalyService`, `PredictiveRiskService`, `NetworkService`, `ReportService`

---

# Table: AuditLog

**Purpose:** System activity audit trail for security and compliance.

| Column | Data Type | Max Length | Mandatory | Unique | Default | Indexed/Searchable |
|--------|-----------|------------|-----------|--------|---------|-------------------|
| log_id | varchar | 100 | No | No | — | — |
| action | varchar | 100 | Yes | No | — | — |
| user | varchar | 50 | Yes | No | — | — |
| target | varchar | 50 | Yes | No | — | — |
| metadata | json | — | No | No | — | — |
| timestamp | datetime | — | Yes | No | — | — |

- **Primary lookup key:** `ROWID`
- **Frequently queried columns:** `user`, `target`, `action`
- **Foreign-key relationships (logical):** References `Officer` via `user` / `target`
- **Used by:** `AdminRepository`

---

# Table: NetworkNode

**Purpose:** Denormalized node entity for criminal network graph visualization.

| Column | Data Type | Max Length | Mandatory | Unique | Default | Indexed/Searchable |
|--------|-----------|------------|-----------|--------|---------|-------------------|
| label | varchar | 150 | Yes | No | — | — |
| node_type | varchar | 50 | Yes | No | — | — |
| entity_type | varchar | 50 | No | No | — | — |
| entity_id | varchar | 50 | No | No | — | — |
| district_id | varchar | 50 | No | No | — | — |
| risk_score | decimal | — | No | No | — | — |
| status | varchar | 20 | No | No | ACTIVE | — |

- **Primary lookup key:** `ROWID`
- **Frequently queried columns:** `node_type`, `entity_type`, `entity_id`, `district_id`
- **Foreign-key relationships (logical):** Semantic links to `Crime`, `Criminal`, `FIR`, `District`, `PoliceStation`, `Officer` via `entity_type` + `entity_id`
- **Used by:** `NetworkRepository`, `SearchRepository`

---

# Table: Anomaly

**Purpose:** Recorded statistical anomaly detection result for districts or stations.

| Column | Data Type | Max Length | Mandatory | Unique | Default | Indexed/Searchable |
|--------|-----------|------------|-----------|--------|---------|-------------------|
| anomaly_type | varchar | 50 | Yes | No | — | — |
| affected_entity_id | varchar | 50 | Yes | No | — | — |
| affected_entity_name | varchar | 255 | Yes | No | — | — |
| severity | varchar | 20 | Yes | No | — | — |
| district_id | varchar | 50 | Yes | No | — | — |
| status | varchar | 20 | No | No | ACTIVE | — |
| description | text | — | No | No | — | — |

- **Primary lookup key:** `ROWID`
- **Frequently queried columns:** `district_id`, `status`, `anomaly_type`
- **Foreign-key relationships (logical):** References `District` via `district_id` / `affected_entity_id`; references `PoliceStation` via `affected_entity_id`
- **Used by:** `AnomalyRepository`, `AnomalyService`, `ReportService`, `SearchRepository`

---

# Table: PredictiveRisk

**Purpose:** Computed deterministic risk prediction record for an entity.

| Column | Data Type | Max Length | Mandatory | Unique | Default | Indexed/Searchable |
|--------|-----------|------------|-----------|--------|---------|-------------------|
| entity_name | varchar | 255 | Yes | No | — | — |
| entity_type | varchar | 50 | Yes | No | — | — |
| risk_score | decimal | — | Yes | No | — | — |
| risk_level | varchar | 20 | Yes | No | — | — |
| district_id | varchar | 50 | Yes | No | — | — |
| status | varchar | 20 | No | No | ACTIVE | — |
| factors_json | json | — | No | No | — | — |

- **Primary lookup key:** `ROWID`
- **Frequently queried columns:** `district_id`, `entity_type`, `entity_name`
- **Foreign-key relationships (logical):** References `District` via `district_id`; semantic references to `PoliceStation` via `entity_type` + `entity_name`
- **Used by:** `PredictiveRiskRepository`, `PredictiveRiskService`, `ReportService`, `SearchRepository`

---

# Table: Search

**Purpose:** Catalyst-backed AI response cache for `ExecutiveIntelligenceService`. Schema is dynamic; rows store arbitrary cached JSON payloads keyed by slug.

| Column | Data Type | Max Length | Mandatory | Unique | Default | Indexed/Searchable |
|--------|-----------|------------|-----------|--------|---------|-------------------|
| ROWID | varchar | 64 | Yes | Yes | — | Primary key |
| (dynamic payload columns) | json/varchar | — | No | No | — | — |

- **Primary lookup key:** `ROWID` (SHA-256 slug)
- **Frequently queried columns:** `ROWID`
- **Foreign-key relationships (logical):** None
- **Used by:** `ExecutiveIntelligenceService` (`ai_service.py`) via raw ZCQL `INSERT INTO Search ...`

---

## Creation Order

Create tables in this order so foreign-key references are resolvable:

1. District
2. PoliceStation
3. Officer
4. Criminal
5. Crime
6. FIR
7. CrimeCriminalLink
8. Report
9. Alert
10. CrimeHotspotCluster
11. PredictionLedger
12. AuditLog
13. User
14. NetworkNode
15. Anomaly
16. PredictiveRisk
17. Search

---

## Minimum Required Columns

For each table, the minimum columns required for the backend to function.

| Table | Minimum Required Columns |
|-------|--------------------------|
| District | `name`, `state`, `code` |
| PoliceStation | `name`, `station_code`, `district_id` |
| Officer | `badge_number`, `name`, `role`, `status` |
| Criminal | `name`, `risk_level`, `status` |
| Crime | `fir_number`, `crime_type`, `title`, `location`, `district_id`, `station_id`, `incident_date`, `status` |
| FIR | `fir_number`, `crime_id`, `district_id`, `station_id`, `officer_id`, `description`, `fir_date`, `status` |
| CrimeCriminalLink | `crime_id`, `criminal_id`, `role` |
| Report | `name`, `report_type`, `created_by_officer_id` |
| Alert | `type`, `severity`, `status`, `message`, `title`, `description`, `source` |
| CrimeHotspotCluster | `cluster_id`, `district_id`, `station_id`, `center_lat`, `center_lon`, `radius_m`, `crime_count`, `period_start`, `period_end`, `scored_at` |
| PredictionLedger | `entity_type`, `entity_id`, `entity_name`, `prediction_type`, `score`, `level`, `model_version`, `scored_at` |
| AuditLog | `action`, `user_id`, `target`, `event_timestamp`, `log_id` |
| NetworkNode | `label`, `node_type`, `status` |
| Anomaly | `anomaly_type`, `affected_entity_id`, `affected_entity_name`, `severity`, `district_id`, `status` |
| PredictiveRisk | `entity_name`, `entity_type`, `risk_score`, `risk_level`, `district_id`, `status` |
| AppUser | `name`, `email`, `role`, `status` |
| Search | `ROWID` |

---

## Bootstrap Seed Order

The exact order `bootstrap()` in `datastore_bootstrap.py` expects:

1. **seed_master_data** (from `app/core/mock_data.py` `_MOCK_DATA`, populated in this dict order at import time):
   1. District
   2. PoliceStation
   3. Criminal
   4. Crime
   5. FIR
   6. CrimeCriminalLink
   7. CrimeHotspotCluster
   8. PredictionLedger
   9. Alert
   10. Report
   11. AuditLog
   12. Officer
   13. User

2. **seed_demo_data** (hardcoded deterministic demo rows):
   1. District
   2. PoliceStation
   3. Officer
   4. Criminal
   5. Crime
   6. CrimeCriminalLink
   7. FIR
   8. Alert
   9. CrimeHotspotCluster
   10. PredictionLedger

3. **create_default_users**:
   1. Officer
   2. User

---

## Officer Table

### Authentication Field Confirmation

Current authentication uses:

- **Login field:** `badge_number`
- **Password field:** `hashed_password`

Authentication does **not** use `email` + `password_hash`.

### Evidence

- `app/services/auth_service.py` line 67:
  `async def login(self, badge_number: str, password: str) -> Dict[str, Any]:`
- `app/repositories/catalyst_officer_repo.py` line 16:
  `async def find_by_badge_number(self, badge_number: str) -> Optional[Dict[str, Any]]:`
- `functions/system_setup/catalyst_bootstrap/datastore_bootstrap.py` demo seed inserts `badge_number` + `hashed_password` and looks up officer by `badge_number` for demo login.
- `email` is stored as a unique indexed string but is never queried by `AuthService.login()`.

### Every Repository and Service That References Officer

| Component | File | How Officer Is Used |
|-----------|------|---------------------|
| `OfficerRepository` | `app/repositories/officer_repo.py` | Queries `Officer` by `user_id`, `catalyst_user_id`, `station_id`, `status`, `badge_number`, `email`, `name`, ROWID |
| `CatalystOfficerRepository` | `app/repositories/catalyst_officer_repo.py` | Queries by `badge_number` (login), `email`, ROWID; creates/updates `hashed_password` |
| `OfficerService` | `app/services/officer_service.py` | CRUD; `sync_catalyst_identity()` provisions officer using `user_id`, `email`, `badge_number` |
| `AuthService` | `app/services/auth_service.py` | `login(badge_number, password)` reads `badge_number` and `hashed_password`; tracks `account_status`, `failed_attempts`, `locked_until`, `last_login` |
| `AdminRepository` | `app/repositories/admin_repo.py` | Joins `User` + `Officer` via `user_id`/`catalyst_user_id` for admin statistics |
| `FIRService` | `app/services/fir_service.py` | Validates `officer_id` existence before FIR creation |
| `ReportService` | `app/services/report_service.py` | Records `created_by_officer_id` in reports |
| `NetworkRepository` | `app/repositories/network_repo.py` | Fetches all `Officer` rows for graph nodes/edges |
| `SearchRepository` | `app/repositories/search_repo.py` | Indirect officer data via `NetworkRepository` |

---

## Verification

- **Total number of tables:** 17
- **Total number of columns (fixed schema):** 136
- **Search table columns:** Dynamic (arbitrary JSON payload + ROWID slug)
- **Total number of tables with SQLAlchemy ORM models:** 6 (`District`, `PoliceStation`, `Officer`, `Crime`, `Alert`, `Report`)

### Inconsistencies Found Between Models, Repositories, and Bootstrap

1. **Crime column naming mismatch**
   - SQLAlchemy model uses `police_station_id` (`app/models/crime.py`)
   - Bootstrap `TABLE_DEFINITIONS` and repositories use `station_id`
   - Repository queries and allowed columns reference `station_id`
   - Impact: ORM model is out of sync with actual Datastore schema

2. **Officer model missing `status`**
   - Bootstrap defines `status` (`varchar(20)`, default `ACTIVE`)
   - SQLAlchemy model does not declare `status`
   - `AdminRepository.get_statistics()` reads `status` from Officer

3. **District model missing columns**
   - Bootstrap defines `status`, `code`
   - SQLAlchemy model does not declare either

4. **PoliceStation model missing `status`**
   - Bootstrap defines `status` (`varchar(20)`, default `ACTIVE`)
   - SQLAlchemy model does not declare `status`

5. **Alert model missing bootstrap columns**
   - Bootstrap columns absent from model: `title`, `description`, `source`, `entity_id`, `entity_type`, `station_id`, `recommended_action`
   - `AlertResponse` schema and repositories query all bootstrap columns

6. **Report model primary key mismatch**
   - SQLAlchemy model declares `id = Column(String, primary_key=True, ...)`
   - Bootstrap/Repository use `ROWID` as the system-generated primary key; `id` is NOT a bootstrap table column

7. **Officer `ALLOWED_COLUMNS` incomplete**
   - `app/repositories/base_repository.py` Officer tuple missing: `district_id`, `jurisdiction_type`, `account_status`, `last_login`, `failed_attempts`, `locked_until`
   - Impact: Any repository method using `_validate_column` against these fields raises `DataValidationError`

8. **Anomaly `ALLOWED_COLUMNS` incomplete**
   - Anomaly tuple missing `affected_entity_id`
   - Impact: Queries filtering on `affected_entity_id` fail validation

9. **AuditLog schema now consistent**
    - Uses `user_id` and `event_timestamp`
    - `ALLOWED_COLUMNS` matches bootstrap `TABLE_DEFINITIONS`

10. **Search table missing from bootstrap `TABLE_DEFINITIONS`**
    - `app/services/ai_service.py` reads/writes `Search` table
    - `TABLE_DEFINITIONS` in `datastore_bootstrap.py` does not include `Search`
    - Impact: If table creation relies solely on bootstrap, `Search` will not be created automatically
