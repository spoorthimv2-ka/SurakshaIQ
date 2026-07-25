import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import bcrypt
import zcatalyst_sdk
from zcatalyst_sdk import CatalystAppError
from zcatalyst_sdk.exceptions import CatalystError, CatalystAPIError
from zcatalyst_sdk._http_client import AuthorizedHttpClient, CredentialUser
from zcatalyst_sdk._constants import RequestMethod

app_logger = logging.getLogger("bootstrap")

DATASCOPE_USER = CredentialUser.USER
DATASCOPE_ADMIN = CredentialUser.ADMIN

TABLE_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "District": {
        "columns": [
            {"column_name": "name", "data_type": "varchar", "max_length": 100, "is_mandatory": True},
            {"column_name": "state", "data_type": "varchar", "max_length": 100, "is_mandatory": True},
            {"column_name": "region_code", "data_type": "varchar", "max_length": 50, "is_mandatory": False},
            {"column_name": "latitude", "data_type": "decimal", "is_mandatory": False, "decimal_digits": 6},
            {"column_name": "longitude", "data_type": "decimal", "is_mandatory": False, "decimal_digits": 6},
            {"column_name": "status", "data_type": "varchar", "max_length": 20, "is_mandatory": False, "default_value": "ACTIVE"},
            {"column_name": "code", "data_type": "varchar", "max_length": 50, "is_mandatory": True, "is_unique": True},
        ]
    },
    "PoliceStation": {
        "columns": [
            {"column_name": "name", "data_type": "varchar", "max_length": 150, "is_mandatory": True},
            {"column_name": "station_code", "data_type": "varchar", "max_length": 50, "is_mandatory": True, "is_unique": True},
            {"column_name": "address", "data_type": "varchar", "max_length": 255, "is_mandatory": False},
            {"column_name": "district_id", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "latitude", "data_type": "decimal", "is_mandatory": False, "decimal_digits": 6},
            {"column_name": "longitude", "data_type": "decimal", "is_mandatory": False, "decimal_digits": 6},
            {"column_name": "status", "data_type": "varchar", "max_length": 20, "is_mandatory": False, "default_value": "ACTIVE"},
        ]
    },
    "Crime": {
        "columns": [
            {"column_name": "fir_number", "data_type": "varchar", "max_length": 100, "is_mandatory": True, "is_unique": True},
            {"column_name": "crime_type", "data_type": "varchar", "max_length": 100, "is_mandatory": True},
            {"column_name": "description", "data_type": "text", "is_mandatory": False},
            {"column_name": "incident_date", "data_type": "datetime", "is_mandatory": True},
            {"column_name": "status", "data_type": "varchar", "max_length": 20, "is_mandatory": False, "default_value": "ACTIVE"},
            {"column_name": "severity", "data_type": "varchar", "max_length": 20, "is_mandatory": False},
            {"column_name": "latitude", "data_type": "decimal", "is_mandatory": False, "decimal_digits": 6},
            {"column_name": "longitude", "data_type": "decimal", "is_mandatory": False, "decimal_digits": 6},
            {"column_name": "address", "data_type": "varchar", "max_length": 255, "is_mandatory": False},
            {"column_name": "district_id", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "station_id", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "title", "data_type": "varchar", "max_length": 255, "is_mandatory": True},
            {"column_name": "location", "data_type": "varchar", "max_length": 100, "is_mandatory": True},
            {"column_name": "victim_name", "data_type": "varchar", "max_length": 100, "is_mandatory": False},
            {"column_name": "suspect_name", "data_type": "varchar", "max_length": 100, "is_mandatory": False},
            {"column_name": "alias", "data_type": "varchar", "max_length": 100, "is_mandatory": False},
            {"column_name": "vehicle_number", "data_type": "varchar", "max_length": 20, "is_mandatory": False},
            {"column_name": "mobile_number", "data_type": "varchar", "max_length": 20, "is_mandatory": False},
            {"column_name": "weapon", "data_type": "varchar", "max_length": 100, "is_mandatory": False},
            {"column_name": "modus_operandi", "data_type": "varchar", "max_length": 100, "is_mandatory": False},
            {"column_name": "keywords", "data_type": "varchar", "max_length": 100, "is_mandatory": False},
            {"column_name": "ipc_sections", "data_type": "varchar", "max_length": 100, "is_mandatory": False},
        ]
    },
    "FIR": {
        "columns": [
            {"column_name": "fir_number", "data_type": "varchar", "max_length": 100, "is_mandatory": True, "is_unique": True},
            {"column_name": "crime_id", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "district_id", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "station_id", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "officer_id", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "description", "data_type": "text", "is_mandatory": True},
            {"column_name": "sections", "data_type": "varchar", "max_length": 100, "is_mandatory": False},
            {"column_name": "summary", "data_type": "text", "is_mandatory": False},
            {"column_name": "fir_date", "data_type": "datetime", "is_mandatory": True},
            {"column_name": "status", "data_type": "varchar", "max_length": 20, "is_mandatory": False, "default_value": "ACTIVE"},
            {"column_name": "victim_name", "data_type": "varchar", "max_length": 100, "is_mandatory": False},
            {"column_name": "suspect_name", "data_type": "varchar", "max_length": 100, "is_mandatory": False},
            {"column_name": "vehicle_number", "data_type": "varchar", "max_length": 20, "is_mandatory": False},
            {"column_name": "mobile_number", "data_type": "varchar", "max_length": 20, "is_mandatory": False},
            {"column_name": "ipc_sections", "data_type": "varchar", "max_length": 100, "is_mandatory": False},
        ]
    },
    "Criminal": {
        "columns": [
            {"column_name": "name", "data_type": "varchar", "max_length": 150, "is_mandatory": True},
            {"column_name": "alias", "data_type": "varchar", "max_length": 100, "is_mandatory": False},
            {"column_name": "age", "data_type": "int", "is_mandatory": False},
            {"column_name": "gender", "data_type": "varchar", "max_length": 10, "is_mandatory": False},
            {"column_name": "last_known_location", "data_type": "varchar", "max_length": 100, "is_mandatory": False},
            {"column_name": "risk_level", "data_type": "varchar", "max_length": 20, "is_mandatory": True},
            {"column_name": "status", "data_type": "varchar", "max_length": 20, "is_mandatory": False, "default_value": "ACTIVE"},
            {"column_name": "photo_url", "data_type": "text", "is_mandatory": False},
        ]
    },
    "Alert": {
        "columns": [
            {"column_name": "type", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "severity", "data_type": "varchar", "max_length": 20, "is_mandatory": True},
            {"column_name": "status", "data_type": "varchar", "max_length": 20, "is_mandatory": False, "default_value": "ACTIVE"},
            {"column_name": "message", "data_type": "text", "is_mandatory": True},
            {"column_name": "district_id", "data_type": "varchar", "max_length": 50, "is_mandatory": False},
            {"column_name": "created_at", "data_type": "datetime", "is_mandatory": False},
            {"column_name": "resolved_at", "data_type": "datetime", "is_mandatory": False},
            {"column_name": "title", "data_type": "varchar", "max_length": 255, "is_mandatory": True},
            {"column_name": "description", "data_type": "text", "is_mandatory": True},
            {"column_name": "source", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "entity_id", "data_type": "varchar", "max_length": 50, "is_mandatory": False},
            {"column_name": "entity_type", "data_type": "varchar", "max_length": 50, "is_mandatory": False},
            {"column_name": "station_id", "data_type": "varchar", "max_length": 50, "is_mandatory": False},
            {"column_name": "recommended_action", "data_type": "text", "is_mandatory": False},
        ]
    },
    "Report": {
        "columns": [
            {"column_name": "name", "data_type": "varchar", "max_length": 255, "is_mandatory": True},
            {"column_name": "report_type", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "parameters_json", "data_type": "json", "is_mandatory": False},
            {"column_name": "created_by_officer_id", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "created_at", "data_type": "datetime", "is_mandatory": False},
        ]
    },
    "Officer": {
        "columns": [
            {"column_name": "catalyst_user_id", "data_type": "varchar", "max_length": 100, "is_mandatory": True, "is_unique": True},
            {"column_name": "name", "data_type": "varchar", "max_length": 150, "is_mandatory": True},
            {"column_name": "email", "data_type": "varchar", "max_length": 255, "is_mandatory": True, "is_unique": True},
            {"column_name": "role", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "rank", "data_type": "varchar", "max_length": 100, "is_mandatory": False},
            {"column_name": "designation", "data_type": "varchar", "max_length": 100, "is_mandatory": False},
            {"column_name": "hashed_password", "data_type": "varchar", "max_length": 255, "is_mandatory": False},
            {"column_name": "badge_number", "data_type": "varchar", "max_length": 50, "is_mandatory": True, "is_unique": True},
            {"column_name": "police_station_id", "data_type": "varchar", "max_length": 50, "is_mandatory": False},
            {"column_name": "district_id", "data_type": "varchar", "max_length": 50, "is_mandatory": False},
            {"column_name": "jurisdiction_type", "data_type": "varchar", "max_length": 20, "is_mandatory": False, "default_value": "STATION"},
            {"column_name": "account_status", "data_type": "varchar", "max_length": 20, "is_mandatory": False, "default_value": "ACTIVE"},
            {"column_name": "last_login", "data_type": "varchar", "max_length": 50, "is_mandatory": False},
            {"column_name": "failed_attempts", "data_type": "int", "is_mandatory": False, "default_value": "0"},
            {"column_name": "locked_until", "data_type": "varchar", "max_length": 50, "is_mandatory": False},
            {"column_name": "status", "data_type": "varchar", "max_length": 20, "is_mandatory": False, "default_value": "ACTIVE"},
        ]
    },
    "User": {
        "columns": [
            {"column_name": "name", "data_type": "varchar", "max_length": 150, "is_mandatory": True},
            {"column_name": "email", "data_type": "varchar", "max_length": 255, "is_mandatory": True, "is_unique": True},
            {"column_name": "role", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "status", "data_type": "varchar", "max_length": 20, "is_mandatory": False, "default_value": "ACTIVE"},
        ]
    },
    "CrimeCriminalLink": {
        "columns": [
            {"column_name": "crime_id", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "criminal_id", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "role", "data_type": "varchar", "max_length": 20, "is_mandatory": False, "default_value": "ACCUSED"},
            {"column_name": "linked_by_officer_id", "data_type": "varchar", "max_length": 50, "is_mandatory": False},
            {"column_name": "linked_at", "data_type": "datetime", "is_mandatory": False},
            {"column_name": "notes", "data_type": "text", "is_mandatory": False},
        ]
    },
    "CrimeHotspotCluster": {
        "columns": [
            {"column_name": "cluster_id", "data_type": "varchar", "max_length": 50, "is_mandatory": True, "is_unique": True},
            {"column_name": "district_id", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "station_id", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "center_lat", "data_type": "decimal", "is_mandatory": True, "decimal_digits": 6},
            {"column_name": "center_lon", "data_type": "decimal", "is_mandatory": True, "decimal_digits": 6},
            {"column_name": "radius_m", "data_type": "int", "is_mandatory": True},
            {"column_name": "crime_count", "data_type": "int", "is_mandatory": True},
            {"column_name": "period_start", "data_type": "datetime", "is_mandatory": True},
            {"column_name": "period_end", "data_type": "datetime", "is_mandatory": True},
            {"column_name": "scored_at", "data_type": "datetime", "is_mandatory": True},
        ]
    },
    "PredictionLedger": {
        "columns": [
            {"column_name": "entity_type", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "entity_id", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "entity_name", "data_type": "varchar", "max_length": 100, "is_mandatory": True},
            {"column_name": "prediction_type", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "score", "data_type": "decimal", "is_mandatory": True, "decimal_digits": 1},
            {"column_name": "level", "data_type": "varchar", "max_length": 20, "is_mandatory": True},
            {"column_name": "factors", "data_type": "json", "is_mandatory": False},
            {"column_name": "model_version", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "scored_at", "data_type": "datetime", "is_mandatory": True},
        ]
    },
    "AuditLog": {
        "columns": [
            {"column_name": "log_id", "data_type": "varchar", "max_length": 100, "is_mandatory": False},
            {"column_name": "action", "data_type": "varchar", "max_length": 100, "is_mandatory": True},
            {"column_name": "user", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "target", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "metadata", "data_type": "json", "is_mandatory": False},
            {"column_name": "timestamp", "data_type": "datetime", "is_mandatory": True},
        ]
    },
    "NetworkNode": {
        "columns": [
            {"column_name": "label", "data_type": "varchar", "max_length": 150, "is_mandatory": True},
            {"column_name": "node_type", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "entity_type", "data_type": "varchar", "max_length": 50, "is_mandatory": False},
            {"column_name": "entity_id", "data_type": "varchar", "max_length": 50, "is_mandatory": False},
            {"column_name": "district_id", "data_type": "varchar", "max_length": 50, "is_mandatory": False},
            {"column_name": "risk_score", "data_type": "decimal", "is_mandatory": False, "decimal_digits": 1},
            {"column_name": "status", "data_type": "varchar", "max_length": 20, "is_mandatory": False, "default_value": "ACTIVE"},
        ]
    },
    "Anomaly": {
        "columns": [
            {"column_name": "anomaly_type", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "affected_entity_id", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "affected_entity_name", "data_type": "varchar", "max_length": 255, "is_mandatory": True},
            {"column_name": "severity", "data_type": "varchar", "max_length": 20, "is_mandatory": True},
            {"column_name": "district_id", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "status", "data_type": "varchar", "max_length": 20, "is_mandatory": False, "default_value": "ACTIVE"},
            {"column_name": "description", "data_type": "text", "is_mandatory": False},
        ]
    },
    "PredictiveRisk": {
        "columns": [
            {"column_name": "entity_name", "data_type": "varchar", "max_length": 255, "is_mandatory": True},
            {"column_name": "entity_type", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "risk_score", "data_type": "decimal", "is_mandatory": True, "decimal_digits": 1},
            {"column_name": "risk_level", "data_type": "varchar", "max_length": 20, "is_mandatory": True},
            {"column_name": "district_id", "data_type": "varchar", "max_length": 50, "is_mandatory": True},
            {"column_name": "status", "data_type": "varchar", "max_length": 20, "is_mandatory": False, "default_value": "ACTIVE"},
            {"column_name": "factors_json", "data_type": "json", "is_mandatory": False},
        ]
    },
}


def _bcrypt_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def verify_connection() -> Any:
    try:
        app_logger.info("[TEMP] About to call zcatalyst_sdk.initialize_app()")
        return zcatalyst_sdk.initialize_app()
    except CatalystAppError as exc:
        raise RuntimeError(f"Catalyst authentication failed: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"Unexpected error during Catalyst initialization: {exc}") from exc


def _get_requester(app) -> Optional[Any]:
    try:
        return app.datastore()._requester
    except Exception:
        return None


def inspect_datastore(app) -> Dict[str, Dict[str, Any]]:
    tables: Dict[str, Dict[str, Any]] = {}
    try:
        ds = app.datastore()
        for t in ds.get_all_tables():
            info = t.to_dict() or {}
            name = info.get("table_name") or ""
            if name:
                tables[name] = info
    except Exception:
        pass
    return tables


def _list_existing_columns(app, table_id_or_name: str) -> List[Dict[str, Any]]:
    cols: List[Dict[str, Any]] = []
    try:
        table = app.datastore().table(table_id_or_name)
        data = table.get_all_columns() or []
        if isinstance(data, dict):
            cols = data.get("data", [])
        elif isinstance(data, list):
            cols = data
        else:
            cols = data if data else []
    except CatalystError:
        pass
    return cols


def check_sdk_capabilities(app) -> Dict[str, bool]:
    caps = {"table_creation": False, "column_creation": False, "schema_inspection": False}
    try:
        inspect_datastore(app)
        caps["schema_inspection"] = True
    except Exception:
        pass
    if _get_requester(app) is not None:
        caps["table_creation"] = True
        caps["column_creation"] = True
    return caps


def _try_create_table(
    requester: AuthorizedHttpClient, table_name: str, columns: List[Dict[str, Any]]
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    payload: Dict[str, Any] = {"table_name": table_name, "table_scope": "GLOBAL", "columns": []}
    body_cols = []
    for c in columns:
        item: Dict[str, Any] = {
            "column_name": c["column_name"],
            "data_type": c["data_type"],
            "is_mandatory": bool(c.get("is_mandatory", False)),
            "is_unique": bool(c.get("is_unique", False)),
            "search_index_enabled": True,
        }
        if c.get("max_length") is not None:
            item["max_length"] = c["max_length"]
        if c.get("default_value") is not None:
            item["default_value"] = c["default_value"]
        if c.get("decimal_digits") is not None:
            item["decimal_digits"] = int(c["decimal_digits"])
        if c.get("data_type") in ("text", "json", "datetime", "date"):
            item["max_length"] = c.get("max_length", 255)
        body_cols.append(item)
    payload["columns"] = body_cols
    try:
        resp = requester.request(
            method=RequestMethod.POST,
            path="/table",
            user=DATASCOPE_ADMIN,
            json=payload,
        )
        data = resp.response_json.get("data") if isinstance(resp.response_json, dict) else None
        if data:
            return True, data
        return True, resp.response_json
    except (CatalystAPIError, CatalystError, Exception):
        return False, None


def create_tables(app, requester, existing: Dict[str, Dict[str, Any]]) -> int:
    created = 0
    for table_name in TABLE_DEFINITIONS:
        if table_name in existing:
            continue
        ok, _ = _try_create_table(requester, table_name, TABLE_DEFINITIONS[table_name]["columns"])
        if ok:
            created += 1
    return created


def _try_create_column(
    requester: AuthorizedHttpClient, table_id_or_name: str, col_def: Dict[str, Any]
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    payload: Dict[str, Any] = {
        "column_name": col_def["column_name"],
        "data_type": col_def["data_type"],
        "is_mandatory": bool(col_def.get("is_mandatory", False)),
        "is_unique": bool(col_def.get("is_unique", False)),
        "search_index_enabled": True,
    }
    if col_def.get("max_length") is not None:
        payload["max_length"] = col_def["max_length"]
    if col_def.get("default_value") is not None:
        payload["default_value"] = col_def["default_value"]
    if col_def.get("decimal_digits") is not None:
        payload["decimal_digits"] = int(col_def["decimal_digits"])
    if col_def.get("data_type") in ("text", "json", "datetime", "date"):
        payload["max_length"] = col_def.get("max_length", 255)
    try:
        resp = requester.request(
            method=RequestMethod.POST,
            path=f"/table/{table_id_or_name}/column",
            user=DATASCOPE_ADMIN,
            json=payload,
        )
        data = resp.response_json.get("data") if isinstance(resp.response_json, dict) else None
        return True, data
    except (CatalystAPIError, CatalystError, Exception):
        return False, None


def create_columns(app, requester, existing: Dict[str, Dict[str, Any]]) -> int:
    created = 0
    for table_name, defn in TABLE_DEFINITIONS.items():
        tbl_info = existing.get(table_name, {})
        tbl_id = tbl_info.get("table_id") or table_name
        existing_cols = _list_existing_columns(app, tbl_id)
        existing_names = {c.get("column_name") for c in existing_cols}
        for c in defn["columns"]:
            if c["column_name"] not in existing_names:
                ok, _ = _try_create_column(requester, tbl_id, c)
                if ok:
                    created += 1
    return created


def _get_table_key(table_name: str) -> Optional[str]:
    mapping = {
        "District": "code",
        "PoliceStation": "station_code",
        "Crime": "fir_number",
        "FIR": "fir_number",
        "Officer": "badge_number",
        "User": "email",
        "CrimeHotspotCluster": "cluster_id",
    }
    return mapping.get(table_name, "ROWID")


def _triage_rows_by_schema(
    table_name: str, rows: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    try:
        mod = __import__(f"app.schemas.{table_name.lower()}", fromlist=["*"])
    except Exception:
        return rows, []
    schema_name = None
    for name in ("Response", "Create", "Base"):
        if hasattr(mod, name):
            schema_name = name
            break
    if not schema_name:
        return rows, []
    try:
        Schema = getattr(mod, schema_name)
    except Exception:
        return rows, []
    valid, invalid = [], []
    for row in rows:
        try:
            Schema.model_validate(row)
            valid.append(row)
        except Exception:
            invalid.append(row)
    return valid, invalid


def _get_mock_data() -> Dict[str, List[Dict[str, Any]]]:
    try:
        from app.core.mock_data import _MOCK_DATA
        return _MOCK_DATA
    except ImportError:
        return {}


def _seed_table(app, table_name: str, rows: List[Dict[str, Any]]) -> Tuple[int, int]:
    table = app.datastore().table(table_name)
    unique_key = _get_table_key(table_name)
    inserted = 0
    skipped = 0
    for row in rows:
        data = dict(row)
        data.setdefault("CREATEDTIME", _now_iso())
        data.setdefault("MODIFIEDTIME", _now_iso())
        try:
            exists = False
            if unique_key == "ROWID":
                rid = data.get("ROWID")
                if rid:
                    existing = table.get_row(rid)
                    if existing:
                        exists = True
            elif unique_key:
                val = data.get(unique_key)
                if val is not None:
                    q = f"SELECT ROWID FROM {table_name} WHERE {unique_key} = '{str(val).replace(chr(39), chr(39)+chr(39))}' LIMIT 1"
                    result = app.zcql().execute_query(q)
                    if result and len(result) > 0:
                        exists = True
            if not exists:
                table.insert_row(data)
                inserted += 1
            else:
                skipped += 1
        except CatalystError:
            pass
    return inserted, skipped


def _row_exists(app, table_name: str, field: str, value: Any) -> bool:
    if value is None:
        return False
    try:
        safe = str(value).replace(chr(39), chr(39) + chr(39))
        q = f"SELECT ROWID FROM {table_name} WHERE {field} = '{safe}' LIMIT 1"
        result = app.zcql().execute_query(q)
        return result and len(result) > 0
    except Exception:
        return False


def seed_master_data(app) -> Tuple[int, int]:
    inserted = 0
    skipped = 0
    data = _get_mock_data()
    for table_name, rows in data.items():
        if not rows:
            continue
        valid, _ = _triage_rows_by_schema(table_name, rows)
        ins, skp = _seed_table(app, table_name, valid)
        inserted += ins
        skipped += skp
    return inserted, skipped


def seed_demo_data(app) -> Tuple[int, int]:
    inserted = 0
    skipped = 0
    try:
        dist_tbl = app.datastore().table("District")
        stn_tbl = app.datastore().table("PoliceStation")
        off_tbl = app.datastore().table("Officer")
        usr_tbl = app.datastore().table("User")
        crm_tbl = app.datastore().table("Criminal")
        crime_tbl = app.datastore().table("Crime")
        link_tbl = app.datastore().table("CrimeCriminalLink")
        fir_tbl = app.datastore().table("FIR")
        alert_tbl = app.datastore().table("Alert")
        hot_tbl = app.datastore().table("CrimeHotspotCluster")
        ledg_tbl = app.datastore().table("PredictionLedger")

        now = _now_iso()

        d1, d2 = None, None
        if not _row_exists(app, "District", "name", "Central District"):
            d1 = dist_tbl.insert_row({"name": "Central District", "state": "Karnataka", "status": "ACTIVE"})
            inserted += 1
        else:
            skipped += 1
        if not _row_exists(app, "District", "name", "North District"):
            d2 = dist_tbl.insert_row({"name": "North District", "state": "Karnataka", "status": "ACTIVE"})
            inserted += 1
        else:
            skipped += 1

        if d1 is None:
            q = "SELECT ROWID FROM District WHERE name = 'Central District' LIMIT 1"
            res = app.zcql().execute_query(q)
            if res and len(res) > 0:
                d1 = res[0].get("District", {})
        if d2 is None:
            q = "SELECT ROWID FROM District WHERE name = 'North District' LIMIT 1"
            res = app.zcql().execute_query(q)
            if res and len(res) > 0:
                d2 = res[0].get("District", {})

        d1rid = d1.get("ROWID", "") if d1 else ""
        d2rid = d2.get("ROWID", "") if d2 else ""

        s1, s2 = None, None
        if d1rid and not _row_exists(app, "PoliceStation", "name", "Central PS"):
            s1 = stn_tbl.insert_row({"name": "Central PS", "district_id": d1rid, "status": "ACTIVE"})
            inserted += 1
        else:
            skipped += 1
        if d2rid and not _row_exists(app, "PoliceStation", "name", "North PS"):
            s2 = stn_tbl.insert_row({"name": "North PS", "district_id": d2rid, "status": "ACTIVE"})
            inserted += 1
        else:
            skipped += 1

        if s1 is None:
            q = "SELECT ROWID FROM PoliceStation WHERE name = 'Central PS' LIMIT 1"
            res = app.zcql().execute_query(q)
            if res and len(res) > 0:
                s1 = res[0].get("PoliceStation", {})
        if s2 is None:
            q = "SELECT ROWID FROM PoliceStation WHERE name = 'North PS' LIMIT 1"
            res = app.zcql().execute_query(q)
            if res and len(res) > 0:
                s2 = res[0].get("PoliceStation", {})

        s1rid = s1.get("ROWID", "") if s1 else ""
        s2rid = s2.get("ROWID", "") if s2 else ""

        demo_email = "demo@karnatakapolice.gov.in"
        demo_badge = "KSP-000001"
        officer_rowid = None
        if not _row_exists(app, "Officer", "badge_number", demo_badge):
            hashed = _bcrypt_hash("Demo@1234")
            o = off_tbl.insert_row({
                "name": "Demo Officer",
                "email": demo_email,
                "badge_number": demo_badge,
                "role": "SYSTEM_ADMINISTRATOR",
                "hashed_password": hashed,
                "police_station_id": s1rid,
                "status": "ACTIVE",
            })
            inserted += 1
            officer_rowid = o.get("ROWID")
        else:
            skipped += 1
            q = f"SELECT ROWID FROM Officer WHERE badge_number = '{str(demo_badge).replace(chr(39), chr(39)+chr(39))}' LIMIT 1"
            res = app.zcql().execute_query(q)
            if res and len(res) > 0:
                officer_rowid = res[0].get("Officer", {}).get("ROWID")

        crime_specs = [
            ("THEFT", d1rid, s1rid, -12.0),
            ("THEFT", d1rid, s1rid, -11.0),
            ("ASSAULT", d1rid, s1rid, -10.0),
            ("ROBBERY", d2rid, s2rid, -9.0),
            ("ASSAULT", d2rid, s2rid, -8.0),
        ]
        crimes = []
        for ctype, did, sid, lat_offset in crime_specs:
            title = f"Demo {ctype} #{len(crimes)+1}"
            c = crime_tbl.insert_row({
                "title": title,
                "crime_type": ctype,
                "description": "Seeded for demo",
                "district_id": did,
                "station_id": sid,
                "status": "ACTIVE",
                "latitude": 12.97 + lat_offset * 0.01,
                "longitude": 77.59 + lat_offset * 0.01,
                "address": f"Seed address {len(crimes)+1}",
            })
            crimes.append(c)
            inserted += 1

        criminals = []
        for i in range(3):
            crm = crm_tbl.insert_row({
                "name": f"Demo Criminal {i+1}",
                "alias": f"Alias {i+1}",
                "risk_level": "HIGH" if i == 0 else "MEDIUM",
                "status": "ACTIVE",
                "last_known_location": "Central District" if i < 2 else "North District",
            })
            criminals.append(crm)
            inserted += 1

        links_created = 0
        for crime in crimes[:3]:
            link_tbl.insert_row({
                "crime_id": crime.get("ROWID", ""),
                "criminal_id": criminals[0].get("ROWID", ""),
                "role": "ACCUSED",
            })
            links_created += 1
        for crime in crimes[3:]:
            link_tbl.insert_row({
                "crime_id": crime.get("ROWID", ""),
                "criminal_id": criminals[1].get("ROWID", ""),
                "role": "ACCUSED",
            })
            links_created += 1
        inserted += links_created

        for i, crime in enumerate(crimes[:3]):
            fir_tbl.insert_row({
                "fir_number": f"FIR-DEMO-{i+1:03d}",
                "crime_id": crime.get("ROWID", ""),
                "district_id": crime.get("district_id", ""),
                "station_id": crime.get("station_id", ""),
                "officer_id": officer_rowid or "",
                "status": "ACTIVE",
                "description": "Seeded FIR",
            })
            inserted += 1

        alert_tbl.insert_row({
            "type": "CRIME_SPIKE",
            "severity": "HIGH",
            "status": "ACTIVE",
            "message": "Demo alert: unusual theft spike in Central District",
            "district_id": d1rid,
        })
        inserted += 1
        alert_tbl.insert_row({
            "type": "ANOMALY",
            "severity": "MEDIUM",
            "status": "ACTIVE",
            "message": "Demo alert: repeat offender activity detected in North PS",
            "district_id": d2rid,
        })
        inserted += 1

        try:
            hot_tbl.insert_row({
                "cluster_id": "CLUSTER-DEMO-1",
                "district_id": d1rid,
                "station_id": s1rid,
                "center_lat": 12.9698,
                "center_lon": 77.5900,
                "radius_m": 1200,
                "crime_count": 3,
                "period_start": now,
                "period_end": now,
                "scored_at": now,
            })
            inserted += 1
        except Exception:
            skipped += 1

        try:
            ledg_tbl.insert_row({
                "entity_type": "District",
                "entity_id": d1rid,
                "entity_name": "Central District",
                "prediction_type": "RISK",
                "score": 45.5,
                "level": "MEDIUM",
                "factors": [],
                "model_version": "v1-seed",
                "scored_at": now,
            })
            inserted += 1
        except Exception:
            skipped += 1
    except Exception:
        pass
    return inserted, skipped


def create_default_users(app) -> Tuple[int, int]:
    districts_tbl = app.datastore().table("District")
    stations_tbl = app.datastore().table("PoliceStation")
    officers_tbl = app.datastore().table("Officer")
    users_tbl = app.datastore().table("User")

    dist_rows = districts_tbl.get_paged_rows(max_rows=100) or {}
    dist_rows = dist_rows.get("data", [])
    if not dist_rows:
        try:
            d = districts_tbl.insert_row({"name": "Default District", "state": "Karnataka", "status": "ACTIVE"})
            dist_rows = [d]
        except Exception:
            return 0, 0

    stn_rows = stations_tbl.get_paged_rows(max_rows=100) or {}
    stn_rows = stn_rows.get("data", [])
    if not stn_rows:
        try:
            s = stations_tbl.insert_row({
                "name": "Default Station",
                "district_id": dist_rows[0].get("ROWID", ""),
                "status": "ACTIVE",
            })
            stn_rows = [s]
        except Exception:
            return 0, 0

    stn_id = stn_rows[0].get("ROWID", "")
    dist_id = dist_rows[0].get("ROWID", "")

    roles = [
        "SYSTEM_ADMINISTRATOR",
        "STATE_COMMAND",
        "DISTRICT_SP",
        "STATION_HOUSE_OFFICER",
        "INVESTIGATING_OFFICER",
        "CID_ANALYST",
    ]
    created = 0
    skipped = 0

    for idx, role in enumerate(roles, start=1):
        badge_number = f"KSP-{idx:06d}"
        name = role.replace("_", " ").title()
        email = f"officer{idx}@suraksha.gov.in"
        password = "Default@123"
        hashed = _bcrypt_hash(password)

        officer_row: Dict[str, Any] = {
            "name": name,
            "email": email,
            "role": role,
            "badge_number": badge_number,
            "status": "ACTIVE",
            "police_station_id": stn_id,
            "hashed_password": hashed,
            "catalyst_user_id": f"USR-{idx:03d}",
            "CREATEDTIME": _now_iso(),
            "MODIFIEDTIME": _now_iso(),
        }
        try:
            is_dup = False
            safe_badge = str(badge_number).replace(chr(39), chr(39) + chr(39))
            q = f"SELECT ROWID FROM Officer WHERE badge_number = '{safe_badge}' LIMIT 1"
            result = app.zcql().execute_query(q)
            if result and len(result) > 0:
                is_dup = True
            if not is_dup:
                officers_tbl.insert_row(officer_row)
                created += 1
            else:
                skipped += 1
        except Exception:
            skipped += 1

        user_row: Dict[str, Any] = {
            "name": name,
            "email": email,
            "role": role,
            "status": "ACTIVE",
            "CREATEDTIME": _now_iso(),
            "MODIFIEDTIME": _now_iso(),
        }
        try:
            is_dup = False
            safe_email = str(email).replace(chr(39), chr(39) + chr(39))
            q = f"SELECT ROWID FROM User WHERE email = '{safe_email}' LIMIT 1"
            result = app.zcql().execute_query(q)
            if result and len(result) > 0:
                is_dup = True
            if not is_dup:
                users_tbl.insert_row(user_row)
                created += 1
            else:
                skipped += 1
        except Exception:
            skipped += 1

    return created, skipped


def verify_integrity(app) -> List[str]:
    errors: List[str] = []
    existing = inspect_datastore(app)
    expected = set(TABLE_DEFINITIONS.keys())
    missing = expected - set(existing.keys())
    if missing:
        errors.append(f"Missing tables after bootstrap: {sorted(missing)}")
    try:
        district_count = len(app.datastore().table("District").get_paged_rows(max_rows=1).get("data", []))
        if district_count == 0:
            errors.append("No districts found in District table")
    except Exception:
        pass
    return errors


def generate_summary(
    sdk_capabilities: Dict[str, bool],
    tables_existing: int,
    tables_created: int,
    rows_inserted: int,
    duplicates_skipped: int,
    errors: List[str],
) -> Dict[str, Any]:
    return {
        "success": True,
        "sdk_capabilities": sdk_capabilities,
        "tables_existing": tables_existing,
        "tables_created": tables_created,
        "rows_inserted": rows_inserted,
        "duplicates_skipped": duplicates_skipped,
        "errors": errors,
    }


def bootstrap() -> Dict[str, Any]:
    app_logger.info("[TEMP] bootstrap() started")
    summary: Dict[str, Any] = {
        "success": False,
        "sdk_capabilities": {},
        "tables_created": 0,
        "tables_existing": 0,
        "rows_inserted": 0,
        "duplicates_skipped": 0,
        "errors": [],
    }
    errors: List[str] = []

    try:
        app_logger.info("[TEMP] About to call verify_connection()")
        app = verify_connection()
        app_logger.info("[TEMP] verify_connection() succeeded")
    except Exception as exc:
        app_logger.error("[TEMP] verify_connection() failed: %s", exc)
        summary["errors"].append(str(exc))
        return summary

    requester = _get_requester(app)
    app_logger.info("[TEMP] About to call check_sdk_capabilities()")
    capabilities = check_sdk_capabilities(app)
    summary["sdk_capabilities"] = capabilities
    app_logger.info("[TEMP] SDK capabilities: %s", capabilities)

    if not capabilities["schema_inspection"]:
        errors.append("Schema inspection is not supported by this SDK.")

    app_logger.info("[TEMP] About to call inspect_datastore()")
    existing = inspect_datastore(app)
    summary["tables_existing"] = len(existing)
    app_logger.info("[TEMP] Existing tables found: %s", len(existing))

    if capabilities["table_creation"] and requester:
        app_logger.info("[TEMP] About to call create_tables()")
        created = create_tables(app, requester, existing)
        summary["tables_created"] = created
        app_logger.info("[TEMP] Tables created: %s", created)
        if created == 0 and len(existing) == 0:
            errors.append("Table creation is supported but no tables were created.")
        app_logger.info("[TEMP] About to call inspect_datastore() again")
        existing = inspect_datastore(app)
    else:
        errors.append("Table creation is not supported by the current Catalyst SDK or runtime.")

    if capabilities["column_creation"] and requester:
        app_logger.info("[TEMP] About to call create_columns()")
        create_columns(app, requester, existing)
    else:
        errors.append("Column creation is not supported by the current Catalyst SDK or runtime.")

    master_ins, master_skp = 0, 0
    demo_ins, demo_skp = 0, 0
    users_ins, users_skp = 0, 0
    try:
        app_logger.info("[TEMP] About to seed_master_data()")
        master_ins, master_skp = seed_master_data(app)
        app_logger.info("[TEMP] seed_master_data() returned: %s, %s", master_ins, master_skp)
    except Exception as exc:
        app_logger.error("[TEMP] seed_master_data() failed: %s", exc)
        errors.append(f"Master data seeding failed: {exc}")

    try:
        app_logger.info("[TEMP] About to seed_demo_data()")
        demo_ins, demo_skp = seed_demo_data(app)
        app_logger.info("[TEMP] seed_demo_data() returned: %s, %s", demo_ins, demo_skp)
    except Exception as exc:
        app_logger.error("[TEMP] seed_demo_data() failed: %s", exc)
        errors.append(f"Demo data seeding failed: {exc}")

    try:
        app_logger.info("[TEMP] About to create_default_users()")
        users_ins, users_skp = create_default_users(app)
        app_logger.info("[TEMP] create_default_users() returned: %s, %s", users_ins, users_skp)
    except Exception as exc:
        app_logger.error("[TEMP] create_default_users() failed: %s", exc)
        errors.append(f"Default user creation failed: {exc}")

    app_logger.info("[TEMP] About to compute summary rows_inserted and duplicates_skipped")
    summary["rows_inserted"] = master_ins + demo_ins + users_ins
    summary["duplicates_skipped"] = master_skp + demo_skp + users_skp

    try:
        app_logger.info("[TEMP] About to call verify_integrity()")
        integrity_errors = verify_integrity(app)
        errors.extend(integrity_errors)
        app_logger.info("[TEMP] verify_integrity() returned %s errors", len(integrity_errors))
    except Exception as exc:
        errors.append(f"Integrity verification failed: {exc}")

    summary["errors"] = errors
    summary["success"] = True
    app_logger.info("[TEMP] bootstrap() completed successfully")
    return summary




