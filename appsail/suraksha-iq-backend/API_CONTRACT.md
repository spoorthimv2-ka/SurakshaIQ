# API Contract — SurakshaIQ Backend (Phase 1)

**Base URL:** `https://<catalyst-app>.zohocatalyst.com/api/v1`  
**Auth:** Bearer JWT (`Authorization: Bearer <access_token>`)  
**Content-Type:** `application/json`

---

## 1. Crimes

### `GET /crimes`
Retrieve paginated crime records with filters.

**Query params:**
| Param | Type | Required | Description |
|---|---|---|---|
| `limit` | int | no | Max 100 |
| `offset` | int | no | Pagination offset |
| `keyword` | string | no | Full-text search on title/description/type |
| `district_id` | string | no | Filter by district ROWID |
| `station_id` | string | no | Filter by police station ROWID |
| `crime_type` | string | no | Filter by crime type |
| `status` | string | no | `ACTIVE` / `INACTIVE` / `ARCHIVED` |
| `date_from` | ISO date | no | Inclusive lower bound on `CREATEDTIME` |
| `date_to` | ISO date | no | Inclusive upper bound on `CREATEDTIME` |

**Response 200:**
```json
[
  {
    "ROWID": "string",
    "title": "string",
    "description": "string",
    "crime_type": "string",
    "location": "string",
    "district_id": "string",
    "station_id": "string",
    "status": "ACTIVE",
    "address": "string",
    "fir_number": "string",
    "latitude": 12.34,
    "longitude": 56.78,
    "CREATEDTIME": "2026-07-24T00:00:00Z",
    "MODIFIEDTIME": "2026-07-24T00:00:00Z"
  }
]
```

### `POST /crimes`
Create a crime record.

**Request body:** `CrimeCreate`  
**Response 201:** `CrimeResponse` (same shape as above plus `ROWID`)

### `PUT /crimes/{id}`
Update a crime record.

**Request body:** `CrimeUpdate`  
**Response 200:** `CrimeResponse`

### `DELETE /crimes/{id}`
Delete a crime record.

**Response 204:** No content

### `GET /crimes/{id}`
Retrieve a single crime.

**Response 200:** `CrimeResponse`

---

## 2. FIRs

### `GET /firs`
Retrieve paginated FIR records with filters.

**Query params:**
| Param | Type | Required | Description |
|---|---|---|---|
| `limit` | int | no | Max 100 |
| `offset` | int | no | Pagination offset |
| `fir_number` | string | no | Full-text search on FIR number |
| `district_id` | string | no | Filter by district |
| `station_id` | string | no | Filter by station |
| `officer_id` | string | no | Filter by investigating officer |
| `status` | string | no | `ACTIVE` / `INACTIVE` / `ARCHIVED` |
| `date_from` | ISO date | no | Lower bound on `fir_date` |
| `date_to` | ISO date | no | Upper bound on `fir_date` |

**Response 200:**
```json
[
  {
    "ROWID": "string",
    "fir_number": "string",
    "crime_id": "string",
    "district_id": "string",
    "station_id": "string",
    "officer_id": "string",
    "description": "string",
    "status": "ACTIVE",
    "fir_date": "2026-07-24T00:00:00Z",
    "sections": "string",
    "summary": "string",
    "CREATEDTIME": "2026-07-24T00:00:00Z",
    "MODIFIEDTIME": "2026-07-24T00:00:00Z"
  }
]
```

### `POST /firs`
Create FIR.

**Request body:** `FIRCreate`  
**Response 201:** `FIRResponse`

### `PUT /firs/{id}`
Update FIR.

**Request body:** `FIRUpdate`  
**Response 200:** `FIRResponse`

### `DELETE /firs/{id}`
Delete FIR.

**Response 204:** No content

### `GET /firs/{id}`
Retrieve single FIR.

**Response 200:** `FIRResponse`

---

## 3. Crime–Criminal Links

### `POST /crime-criminal-links/`
Explicitly link a criminal to a crime.

**Request body:**
```json
{
  "crime_id": "string",
  "criminal_id": "string",
  "role": "ACCUSED",
  "notes": "string"
}
```

**Response 201:**
```json
{
  "ROWID": "string",
  "crime_id": "string",
  "criminal_id": "string",
  "role": "ACCUSED",
  "notes": "string",
  "linked_by_officer_id": "string",
  "linked_at": "2026-07-24T00:00:00Z",
  "CREATEDTIME": "2026-07-24T00:00:00Z",
  "MODIFIEDTIME": "2026-07-24T00:00:00Z"
}
```

### `GET /crime-criminal-links/crime/{crime_id}`
List all criminals linked to a crime.

**Query params:** `limit` (default 100), `offset` (default 0)  
**Response 200:** `List[CrimeCriminalLinkResponse]`

### `GET /crime-criminal-links/criminal/{criminal_id}`
List all crimes linked to a criminal.

**Query params:** `limit` (default 100), `offset` (default 0)  
**Response 200:** `List[CrimeCriminalLinkResponse]`

### `DELETE /crime-criminal-links/{link_id}`
Remove an explicit link.

**Response 204:** No content

---

## 4. Hotspots

### `GET /hotspots`
Retrieve hotspot records aggregated by district + station.

**Query params:**
| Param | Type | Required | Description |
|---|---|---|---|
| `limit` | int | no | Max 100 |
| `district_id` | string | no | Filter by district |
| `station_id` | string | no | Filter by station |
| `crime_type` | string | no | Filter by crime type |
| `status` | string | no | Filter by status |
| `start_date` | ISO date | no | Start of analysis window |
| `end_date` | ISO date | no | End of analysis window |

**Response 200:**
```json
[
  {
    "id": "string",
    "district": "string",
    "police_station": "string",
    "crime_count": 0,
    "hotspot_score": 0.0,
    "severity": "LOW",
    "latest_crime_date": "2026-07-24"
  }
]
```

### `GET /hotspots/districts`
Retrieve hotspot summary per district.

**Query params:** `start_date`, `end_date`  
**Response 200:**
```json
[
  {
    "district_id": "string",
    "district_name": "string",
    "total_crimes": 0,
    "hotspot_score": 0.0,
    "active_firs": 0,
    "trend": "stable"
  }
]
```

### `GET /hotspots/stations`
Retrieve hotspot summary per police station.

**Query params:** `start_date`, `end_date`  
**Response 200:**
```json
[
  {
    "station_id": "string",
    "station_name": "string",
    "district_id": "string",
    "district_name": "string",
    "crime_count": 0,
    "hotspot_score": 0.0,
    "active_firs": 0
  }
]
```

### `GET /hotspots/top`
Retrieve top-ranked hotspots.

**Query params:** `limit` (default 10), `start_date`, `end_date`  
**Response 200:** Same as `GET /hotspots`

### `GET /hotspots/summary`
Retrieve aggregated hotspot summary counts.

**Query params:** `start_date`, `end_date`  
**Response 200:**
```json
{
  "total_hotspots": 0,
  "high_severity_count": 0,
  "medium_severity_count": 0,
  "low_severity_count": 0
}
```

---

## 5. Network Analysis

### `GET /network`
Retrieve the full relationship graph.

**Query params:** `limit` (default 500)  
**Response 200:**
```json
{
  "nodes": [
    { "id": "string", "label": "string", "type": "string", "properties": {} }
  ],
  "edges": [
    { "source": "string", "target": "string", "type": "string", "properties": {} }
  ],
  "statistics": {
    "total_nodes": 0,
    "total_edges": 0,
    "connected_offenders": 0,
    "connected_stations": 0,
    "connected_districts": 0,
    "average_connections": 0.0
  },
  "metadata": {}
}
```

### `GET /network/statistics`
Retrieve network statistics only.

**Response 200:** `NetworkStatistics`

### `GET /network/offenders/{offender_id}`
Retrieve subgraph for a specific offender.

**Response 200:** `NetworkGraphResponse`

### `GET /network/stations/{station_id}`
Retrieve subgraph for a specific station.

**Response 200:** `NetworkGraphResponse`

### `GET /network/districts/{district_id}`
Retrieve subgraph for a specific district.

**Response 200:** `NetworkGraphResponse`

### `GET /network/search`
Full-text search across network nodes.

**Query params:** `q` (string, required), `limit` (default 50)  
**Response 200:**
```json
{
  "query": "string",
  "nodes": [],
  "edges": []
}
```

---

## 6. Repeat Offenders

### `GET /repeat-offenders`
Retrieve repeat offenders with optional filters. Defaults to explicit `CrimeCriminalLink` linkage.

**Query params:**
| Param | Type | Required | Description |
|---|---|---|---|
| `limit` | int | no | Max 100 |
| `offset` | int | no | Pagination offset |
| `district_id` | string | no | Filter by district |
| `station_id` | string | no | Filter by station |
| `crime_type` | string | no | Filter by crime type |
| `start_date` | ISO datetime | no | Lower bound |
| `end_date` | ISO datetime | no | Upper bound |
| `minimum_offences` | int | no | Default 1 |
| `include_heuristic` | bool | no | If true, fall back to district-proximity inference |

**Response 200:**
```json
[
  {
    "offender_id": "string",
    "offender_name": "string",
    "total_offences": 0,
    "fir_count": 0,
    "districts_involved": ["string"],
    "police_stations_involved": ["string"],
    "latest_offence": "2026-07-24",
    "repeat_offender_score": 0.0
  }
]
```

### `GET /repeat-offenders/top`
Retrieve top-ranked repeat offenders.

**Query params:** `limit` (default 10), `start_date`, `end_date`, `include_heuristic`  
**Response 200:** Same as `GET /repeat-offenders`

### `GET /repeat-offenders/{offender_id}`
Retrieve detailed offender information.

**Query params:** `include_heuristic` (bool, default false)  
**Response 200:**
```json
{
  "offender_id": "string",
  "offender_name": "string",
  "alias": "string",
  "age": 0,
  "last_known_location": "string",
  "risk_level": "string",
  "status": "ACTIVE",
  "total_offences": 0,
  "fir_count": 0,
  "districts_involved": ["string"],
  "police_stations_involved": ["string"],
  "latest_offence": "2026-07-24",
  "repeat_offender_score": 0.0,
  "crime_categories": ["string"],
  "offence_timeline": [
    {
      "crime_id": "string",
      "crime_type": "string",
      "district_id": "string",
      "station_id": "string",
      "offence_date": "2026-07-24",
      "fir_number": "string"
    }
  ]
}
```

### `GET /repeat-offenders/statistics`
Retrieve aggregated repeat offender statistics.

**Query params:** `start_date`, `end_date`, `include_heuristic`  
**Response 200:**
```json
{
  "total_repeat_offenders": 0,
  "average_offences": 0.0,
  "highest_offence_count": 0,
  "district_with_most_repeat_offenders": "string",
  "repeat_offender_distribution": [
    { "district": "string", "repeat_offender_count": 0 }
  ]
}
```

---

## 7. Predictive Risk

### `GET /predictive-risk`
Retrieve risk predictions for all districts and stations.

**Query params:** `limit` (default 100)  
**Response 200:**
```json
[
  {
    "entity_id": "string",
    "entity_type": "District",
    "entity_name": "string",
    "risk_score": 0.0,
    "risk_level": "LOW",
    "contributing_factors": [
      { "name": "string", "weight": 0.0, "contribution": 0.0 }
    ],
    "last_updated": "2026-07-24T00:00:00Z"
  }
]
```

### `GET /predictive-risk/summary`
Retrieve aggregated risk summary.

**Response 200:**
```json
{
  "total_entities": 0,
  "average_risk": 0.0,
  "highest_risk_district": "string",
  "highest_risk_station": "string",
  "total_high_risk": 0,
  "total_critical_risk": 0,
  "risk_distribution": [
    {
      "entity_id": "string",
      "entity_type": "string",
      "entity_name": "string",
      "risk_score": 0.0,
      "risk_level": "LOW"
    }
  ]
}
```

### `GET /predictive-risk/districts`
Retrieve risk scores for all districts.

**Response 200:**
```json
[
  {
    "district_id": "string",
    "district_name": "string",
    "risk_score": 0.0,
    "risk_level": "LOW",
    "crime_count": 0,
    "fir_count": 0,
    "hotspot_score": 0.0,
    "repeat_offender_count": 0,
    "contributing_factors": []
  }
]
```

### `GET /predictive-risk/stations`
Retrieve risk scores for all police stations.

**Response 200:**
```json
[
  {
    "station_id": "string",
    "station_name": "string",
    "district_id": "string",
    "district_name": "string",
    "risk_score": 0.0,
    "risk_level": "LOW",
    "crime_count": 0,
    "fir_count": 0,
    "hotspot_score": 0.0,
    "contributing_factors": []
  }
]
```

### `GET /predictive-risk/{entity_id}`
Retrieve risk for a specific entity.

**Query params:** `entity_type` (default `District`)  
**Response 200:** `RiskPrediction`

---

## 8. Anomalies

### `GET /anomaly`
Retrieve detected anomalies.

**Query params:** `limit` (default 100)  
**Response 200:**
```json
[
  {
    "anomaly_id": "string",
    "anomaly_type": "string",
    "severity": "LOW",
    "affected_entity_id": "string",
    "affected_entity_type": "string",
    "affected_entity_name": "string",
    "anomaly_score": 0.0,
    "contributing_factors": [],
    "description": "string",
    "detected_at": "2026-07-24T00:00:00Z"
  }
]
```

### `GET /anomaly/summary`
Retrieve aggregated anomaly summary.

**Response 200:**
```json
{
  "total_anomalies": 0,
  "high_anomalies": 0,
  "critical_anomalies": 0,
  "affected_districts": 0,
  "affected_stations": 0,
  "average_anomaly_score": 0.0,
  "anomaly_distribution": []
}
```

### `GET /anomaly/districts`
Retrieve anomalies aggregated by district.

**Response 200:**
```json
[
  {
    "district_id": "string",
    "district_name": "string",
    "anomaly_score": 0.0,
    "severity": "LOW",
    "crime_count": 0,
    "fir_count": 0,
    "hotspot_score": 0.0,
    "contributing_factors": []
  }
]
```

### `GET /anomaly/stations`
Retrieve anomalies aggregated by station.

**Response 200:**
```json
[
  {
    "station_id": "string",
    "station_name": "string",
    "district_id": "string",
    "district_name": "string",
    "anomaly_score": 0.0,
    "severity": "LOW",
    "crime_count": 0,
    "fir_count": 0,
    "hotspot_score": 0.0,
    "contributing_factors": []
  }
]
```

### `GET /anomaly/{anomaly_id}`
Retrieve a specific anomaly.

**Response 200:** `Anomaly`

---

## 9. Prediction Ledger (immutable history)

### `GET /prediction-ledger`
Retrieve historical prediction entries.

**Query params:**
| Param | Type | Required | Description |
|---|---|---|---|
| `entity_type` | string | no | `District` / `PoliceStation` / `Offender` / `Summary` |
| `entity_id` | string | no | ROWID or key of the target |
| `prediction_type` | string | no | `HOTSPOT` / `RISK` / `ANOMALY` / `REPEAT_OFFENDER` |
| `limit` | int | no | Default 100 |
| `offset` | int | no | Pagination offset |

**Response 200:**
```json
[
  {
    "ROWID": "string",
    "entity_type": "District",
    "entity_id": "string",
    "entity_name": "string",
    "prediction_type": "RISK",
    "score": 0.0,
    "level": "LOW",
    "factors": [],
    "model_version": "v1-heuristic",
    "scored_at": "2026-07-24T00:00:00Z",
    "CREATEDTIME": "2026-07-24T00:00:00Z"
  }
]
```

---

## Shared Behaviors

- **Pagination** uses `limit` / `offset` query params. Zero-based offset.
- **Sorting** defaults to `CREATEDTIME DESC`. Column names are validated against an allowlist.
- **Errors:** `400` for validation, `401` for auth, `403` for RBAC, `404` for not found, `500` for repository failures, `503` for Catalyst unavailability.
- **Timestamps** are ISO-8601 strings in UTC unless otherwise noted.

---

## Phase 1 Non-Goals (noted for frontend planning)

The following are out of scope for Phase 1 and must not be called by the frontend yet:

- `POST /analytics/hotspots/run` (cluster computation trigger)
- `GET /analytics/hotspots/clusters` (GeoJSON clusters)
- `GET /analytics/hotspots/timeseries`
- `GET /analytics/hotspots/forecast`
- `GET /analytics/network/centrality`
- `GET /analytics/network/communities`
- `GET /analytics/network/path`
- `POST /predictions/retrain`
- `GET /anomalies/{id}/explain`
- `GET /ml/health`

Frontend types should assume these paths do not exist until explicitly released.
