import re
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone, timedelta


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_row(overrides: Dict[str, Any]) -> Dict[str, Any]:
    base = {
        "ROWID": overrides.pop("ROWID", ""),
        "CREATEDTIME": overrides.pop("CREATEDTIME", _now_iso()),
        "MODIFIEDTIME": overrides.pop("MODIFIEDTIME", _now_iso()),
    }
    base.update(overrides)
    return base


_MOCK_DATA: Dict[str, List[Dict[str, Any]]] = {
    "District": [],
    "PoliceStation": [],
    "Crime": [],
    "FIR": [],
    "Criminal": [],
    "Alert": [],
    "Report": [],
    "Officer": [],
    "User": [],
    "CrimeCriminalLink": [],
    "CrimeHotspotCluster": [],
    "PredictionLedger": [],
    "AuditLog": [],
}

_DISTRICTS = [
    ("bangalore-urban", "Bangalore Urban", 12.9716, 77.5946),
    ("bangalore-rural", "Bangalore Rural", 13.1000, 77.5000),
    ("mysuru", "Mysuru", 12.2958, 76.6394),
    ("belagavi", "Belagavi", 15.8497, 74.4977),
    ("mangaluru", "Mangaluru", 12.9178, 74.8560),
    ("hubli-dharwad", "Hubballi-Dharwad", 15.3647, 75.1390),
    ("kalaburagi", "Kalaburagi", 17.3297, 76.8343),
    ("davanagere", "Davanagere", 14.4540, 75.9218),
    ("ballari", "Ballari", 15.1394, 76.9214),
    ("vijayapura", "Vijayapura", 16.8300, 75.7100),
    ("shivamogga", "Shivamogga", 13.9299, 75.5681),
    ("hassan", "Hassan", 13.0072, 76.1004),
    ("udupi", "Udupi", 13.3409, 74.7471),
    ("chamarajanagar", "Chamarajanagar", 11.9261, 76.9393),
    ("gadag", "Gadag", 15.4298, 75.6274),
    ("kolar", "Kolar", 13.1371, 78.1266),
    ("tumakuru", "Tumakuru", 13.3392, 77.1010),
    ("raichur", "Raichur", 16.2076, 77.3463),
    ("bidar", "Bidar", 17.9103, 77.5199),
    ("yadgir", "Yadgir", 16.7700, 77.1400),
]

_CRIME_TYPES = [
    "theft", "robbery", "assault", "cybercrime", "narcotics",
    "murder", "rape", "kidnapping", "burglary", "fraud"
]

_STATUSES = ["open", "under-investigation", "closed", "unsolved"]
_SEVERITIES = ["low", "medium", "high", "critical"]

_TITLE_TEMPLATES = [
    "Wallet stolen at {loc}", "Mobile snatching near {loc}", "Burglary at {loc}",
    "Assault near {loc}", "Chain snatching at {loc}", "Shop theft at {loc}",
    "House break-in at {loc}", "Online fraud complaint from {loc}",
    "Cyber fraud at {loc}", "Drug seizure near {loc}",
    "Vehicle theft at {loc}", "Pickpocketing at {loc}", "Robbery at {loc}",
    "Harassment near {loc}", "Missing complaint from {loc}",
]

_DESC_TEMPLATES = [
    "Incident reported by victim around {time}.",
    "Patrol team responded and collected evidence.",
    "Case registered under IPC sections.",
    "Witness statement recorded.",
    "Investigation ongoing.",
]


def _add(did: str, dname: str, lat: float, lon: float) -> None:
    _MOCK_DATA["District"].append(_make_row({
        "ROWID": f"DIST-{did}",
        "name": dname,
        "state": "Karnataka",
        "region_code": f"KA-{did}",
        "latitude": lat,
        "longitude": lon,
        "status": "active",
        "code": f"KD{did}",
    }))


def _seed_large_dataset() -> None:
    dist_ids = []
    dist_map = {}
    for code, name, lat, lon in _DISTRICTS:
        _MOCK_DATA["District"].append(_make_row({
            "ROWID": code,
            "name": name,
            "state": "Karnataka",
            "region_code": f"KA-{code}",
            "latitude": lat,
            "longitude": lon,
            "status": "active",
            "code": code,
        }))
        dist_ids.append(code)
        dist_map[code] = {"ROWID": code, "name": name, "latitude": lat, "longitude": lon}

    station_counter = 1
    for did in dist_ids:
        for suffix in ["north", "south", "east", "west"]:
            lat = dist_map[did]["latitude"] + (0.02 if suffix == "north" else -0.02 if suffix == "south" else 0.0)
            lon = dist_map[did]["longitude"] + (0.02 if suffix == "east" else -0.02 if suffix == "west" else 0.0)
            _MOCK_DATA["PoliceStation"].append(_make_row({
                "ROWID": f"STN-{str(station_counter).zfill(3)}",
                "name": f"{dist_map[did]['name']} {suffix.title()} Station",
                "station_code": f"STN-{str(station_counter).zfill(3)}",
                "address": f"{dist_map[did]['name']} {suffix.title()} area",
                "district_id": did,
                "latitude": lat,
                "longitude": lon,
                "status": "active",
            }))
            station_counter += 1

    stations = _MOCK_DATA["PoliceStation"]
    stn_map: Dict[str, List[Dict[str, Any]]] = {}
    for s in stations:
        stn_map.setdefault(s["district_id"], []).append(s)

    rng = __import__("random").Random(42)
    start_dt = datetime(2022, 1, 1, tzinfo=timezone.utc)
    end_dt = datetime(2024, 12, 31, tzinfo=timezone.utc)
    delta = (end_dt - start_dt).total_seconds()

    crime_types = _CRIME_TYPES
    statuses = _STATUSES
    severities = _SEVERITIES
    locations = ["Main Market", "Bus Stand", "Temple Rd", "College Rd", "Railway Stn", "IT Park", "Bridge", "Park", "Colony", "Market"]
    victim_names = ["Rahul", "Ravi", "Priya", "Anita", "Suresh", "Kavitha", "Manoj", "Deepa", "Arun", "Lakshmi", "Ramesh", "Sunita", "Vijay", "Geetha", "Kiran"]
    suspect_names = ["Rahul", "Ravi", "Priya", "Anita", "Suresh", "Kavitha", "Manoj", "Deepa", "Arun", "Lakshmi", "Ramesh", "Sunita", "Vijay", "Geetha", "Kiran"]
    aliases = ["Ricky", "Danny", "Bunty", "Monty", "Sonu", "Tiger", "Munna", "Pintu", "Babloo", "Rinku", "Chhotu", "Golu", "Sweety", "Pappu", "Bittu"]
    vehicle_numbers = ["KA01AB1234", "KA02CD5678", "KA03EF9012", "KA04GH3456", "KA05IJ7890", "KA06KL1234", "KA07MN5678", "KA08OP9012", "KA09QR3456", "KA10ST7890"]
    mobile_numbers = ["9876543210", "9876543211", "9876543212", "9876543213", "9876543214", "9876543215", "9876543216", "9876543217", "9876543218", "9876543219"]
    weapons = ["Knife", "Pistol", "Wooden stick", "Iron rod", "Chain", "Stone", "Hammer", "Screwdriver", "Gun", "Blunt object"]
    modus_operandis = ["Snatching", "Burglary", "Fraud", "Impersonation", "Online scam", "Extortion", "Abduction", "Harassment", "Theft", "Robbery"]
    keywords = ["Bribery", "Rape", "Cybercrime", "Theft", "Kidnapping", "Murder", "Assault", "Robbery", "Fraud", "Narcotics"]

    def rand_ts() -> str:
        return (start_dt + timedelta(seconds=rng.uniform(0, delta))).isoformat()

    def rand_loc(did: str) -> tuple[float, float]:
        base = dist_map[did]
        return base["latitude"] + rng.uniform(-0.05, 0.05), base["longitude"] + rng.uniform(-0.05, 0.05)

    crime_counter = 1
    fir_counter = 1
    criminal_counter = 1
    alert_counter = 1
    link_counter = 1
    cluster_counter = 1
    ledger_counter = 1

    district_station_pairs: List[tuple] = []
    for did in dist_ids:
        for s in stn_map.get(did, []):
            district_station_pairs.append((did, s["ROWID"]))

    if not district_station_pairs:
        district_station_pairs = [("bangalore-urban", "STN-001")]

    criminals_created = 0
    for _ in range(500):
        sex = rng.choice(["MALE", "FEMALE"])
        age = rng.randint(18, 65)
        risk = rng.choice(["low", "medium", "high", "critical"])
        stat = rng.choice(["open", "under-investigation", "closed", "unsolved"])
        did = rng.choice(dist_ids)
        _MOCK_DATA["Criminal"].append(_make_row({
            "ROWID": f"CRMNL-{str(criminal_counter).zfill(3)}",
            "name": f"Person {criminal_counter}",
            "alias": f"Alias{criminal_counter}",
            "age": age,
            "gender": sex,
            "last_known_location": did,
            "risk_level": risk.upper() if rng.random() < 0.5 else risk,
            "status": stat,
            "photo_url": "",
        }))
        criminal_counter += 1
        criminals_created += 1

    for _ in range(8000):
        did, sid = rng.choice(district_station_pairs)
        ctype = rng.choice(crime_types)
        stat = rng.choices(statuses, weights=[40, 30, 20, 10], k=1)[0]
        sev = rng.choices(severities, weights=[30, 30, 25, 15], k=1)[0]
        lat, lon = rand_loc(did)
        loc = rng.choice(locations)
        title = rng.choice(_TITLE_TEMPLATES).format(loc=loc)
        desc = rng.choice(_DESC_TEMPLATES).format(time=f"{rng.randint(0,23):02d}:{rng.randint(0,59):02d}")
        ts = rand_ts()
        fir_num = f"FIR-{ts[:4]}-{str(crime_counter).zfill(4)}"
        sec = rng.choice(["IPC 379", "IPC 323", "IPC 302", "IPC 376", "IPC 420", "IPC 506", "IPC 120B", "IT Act", "NDPS Act"])

        _MOCK_DATA["Crime"].append(_make_row({
            "ROWID": f"CRM-{str(crime_counter).zfill(3)}",
            "fir_number": fir_num,
            "crime_type": ctype,
            "description": desc,
            "incident_date": ts[:10],
            "status": stat,
            "severity": sev,
            "latitude": lat,
            "longitude": lon,
            "address": f"{loc}, {dist_map[did]['name']}",
            "district_id": did,
            "station_id": sid,
            "title": title,
            "location": loc,
            "victim_name": rng.choice(victim_names),
            "suspect_name": rng.choice(suspect_names),
            "alias": rng.choice(aliases),
            "vehicle_number": rng.choice(vehicle_numbers) if rng.random() < 0.3 else "",
            "mobile_number": rng.choice(mobile_numbers) if rng.random() < 0.4 else "",
            "weapon": rng.choice(weapons) if ctype in ("murder", "assault", "robbery") else "",
            "modus_operandi": rng.choice(modus_operandis),
            "keywords": rng.choice(keywords),
            "ipc_sections": sec if rng.random() < 0.6 else "",
            "CREATEDTIME": ts,
        }))

        if rng.random() < 0.75:
            sec = rng.choice(["IPC 379", "IPC 323", "IPC 302", "IPC 376", "IPC 420", "IPC 506", "IPC 120B", "IT Act", "NDPS Act"])
            summary = f"Case registered under {sec}."
            _MOCK_DATA["FIR"].append(_make_row({
                "ROWID": f"FIR-{str(fir_counter).zfill(4)}",
                "fir_number": fir_num,
                "crime_id": f"CRM-{str(crime_counter).zfill(3)}",
                "station_id": sid,
                "officer_id": f"OFF-{str(rng.randint(1, 5)).zfill(3)}",
                "description": desc,
                "sections": sec,
                "summary": summary,
                "fir_date": ts[:10],
                "status": stat,
                "district_id": did,
                "victim_name": rng.choice(victim_names),
                "suspect_name": rng.choice(suspect_names),
                "vehicle_number": rng.choice(vehicle_numbers) if rng.random() < 0.2 else "",
                "mobile_number": rng.choice(mobile_numbers) if rng.random() < 0.3 else "",
                "ipc_sections": sec,
                "CREATEDTIME": ts,
            }))
            fir_counter += 1

        if rng.random() < 0.4 and criminals_created > 0:
            crm = rng.choice(_MOCK_DATA["Criminal"])
            note = rng.choice(["Identified via CCTV", "Witness identification", "Mobile forensics", "Patrol team found", "Accomplice identified"])
            _MOCK_DATA["CrimeCriminalLink"].append(_make_row({
                "ROWID": f"LINK-{str(link_counter).zfill(4)}",
                "crime_id": f"CRM-{str(crime_counter).zfill(3)}",
                "criminal_id": crm["ROWID"],
                "role": rng.choice(["ACCUSED", "ACCOMPLICE", "WITNESS"]),
                "linked_by_officer_id": f"OFF-{str(rng.randint(1, 5)).zfill(3)}",
                "linked_at": ts,
                "notes": note,
            }))
            link_counter += 1

        if rng.random() < 0.15:
            _MOCK_DATA["CrimeHotspotCluster"].append(_make_row({
                "ROWID": f"HOT-{str(cluster_counter).zfill(3)}",
                "cluster_id": f"CL-{str(cluster_counter).zfill(3)}",
                "district_id": did,
                "station_id": sid,
                "center_lat": lat,
                "center_lon": lon,
                "radius_m": rng.randint(100, 1000),
                "crime_count": rng.randint(1, 20),
                "period_start": ts[:10],
                "period_end": ts[:10],
                "scored_at": ts,
            }))
            cluster_counter += 1

        if rng.random() < 0.05:
            _MOCK_DATA["PredictionLedger"].append(_make_row({
                "ROWID": f"LEDGER-{str(ledger_counter).zfill(3)}",
                "entity_type": rng.choice(["PoliceStation", "District"]),
                "entity_id": sid if rng.random() < 0.5 else did,
                "entity_name": sid if rng.random() < 0.5 else did,
                "prediction_type": rng.choice(["HOTSPOT", "RISK"]),
                "score": round(rng.uniform(0, 100), 1),
                "level": rng.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]).upper(),
                "factors": [],
                "model_version": "v1-heuristic",
                "scored_at": ts,
                "CREATEDTIME": ts,
            }))
            ledger_counter += 1
        crime_counter += 1

    for _ in range(200):
        did = rng.choice(dist_ids)
        sev = rng.choices(["low", "medium", "high", "critical"], weights=[20, 30, 35, 15], k=1)[0]
        stat = rng.choice(["open", "under-investigation", "closed", "unsolved"])
        atype = rng.choice(["CRIME_SPIKE", "ASSAULT_ALERT", "CYBER_ALERT", "HOTSPOT_ALERT", "BURGLARY_ALERT"])
        _MOCK_DATA["Alert"].append(_make_row({
            "ROWID": f"ALT-{str(alert_counter).zfill(3)}",
            "type": atype,
            "severity": sev.upper(),
            "status": stat,
            "message": f"Alert for {dist_map[did]['name']} area",
            "district_id": did,
            "created_at": rand_ts(),
            "resolved_at": _now_iso() if rng.random() < 0.3 else None,
            "title": f"{dist_map[did]['name']} Alert",
            "description": f"Alert message for {dist_map[did]['name']}",
            "source": "SYSTEM",
            "entity_id": rng.choice([did, rng.choice(stn_map.get(did, []))["ROWID"]] if stn_map.get(did) else [did]),
            "entity_type": rng.choice(["District", "PoliceStation"]),
            "recommended_action": rng.choice(["Deploy patrols", "Increase surveillance", "Issue advisory", "Night patrolling", "Immediate investigation"]),
        }))
        alert_counter += 1

    for i in range(1, 4):
        _MOCK_DATA["Report"].append(_make_row({
            "ROWID": f"RPT-{str(i).zfill(3)}",
            "name": f"Report {i}",
            "report_type": rng.choice(["CRIME_SUMMARY", "DISTRICT_REPORT", "HOTSPOT_ANALYSIS"]),
            "parameters_json": "{}",
            "created_by_officer_id": f"OFF-{str(rng.randint(1, 5)).zfill(3)}",
            "created_at": rand_ts(),
            "status": "active",
        }))

    for i in range(1, 11):
        _MOCK_DATA["AuditLog"].append(_make_row({
            "ROWID": f"AUDIT-{str(i).zfill(3)}",
            "action": rng.choice(["LOGIN", "LOGOUT", "CREATE_FIR", "UPDATE_CASE", "SEARCH"]),
            "user": f"OFF-{str(rng.randint(1, 5)).zfill(3)}",
            "target": f"OFF-{str(rng.randint(1, 5)).zfill(3)}",
            "metadata": {"ip": "127.0.0.1"},
            "created_at": rand_ts(),
        }))

    for i in range(1, 21):
        did = rng.choice(dist_ids)
        _MOCK_DATA["Officer"].append(_make_row({
            "ROWID": f"OFF-{str(i).zfill(3)}",
            "catalyst_user_id": f"USR-{str(i).zfill(3)}",
            "name": f"Officer {i}",
            "email": f"officer{i}@suraksha.test",
            "role": rng.choice(["STATION_HOUSE_OFFICER", "INVESTIGATING_OFFICER", "CID_ANALYST", "DISTRICT_SP"]),
            "rank": rng.choice(["Inspector", "Sub Inspector", "Assistant Sub Inspector", "Constable"]),
            "designation": "Police",
            "hashed_password": None,
            "police_station_id": rng.choice(stn_map.get(did, [{"ROWID": "STN-001"}]))["ROWID"],
            "status": "active",
        }))
        _MOCK_DATA["User"].append(_make_row({
            "ROWID": f"USR-{str(i).zfill(3)}",
            "name": f"Officer {i}",
            "email": f"officer{i}@suraksha.test",
            "role": rng.choice(["OFFICER", "ANALYST", "ADMIN"]),
            "status": "active",
        }))


_seed_large_dataset()


class MockTable:
    def __init__(self, table_name: str):
        self.table_name = table_name

    def insert_row(self, data: Dict[str, Any]) -> Dict[str, Any]:
        rows = _MOCK_DATA.setdefault(self.table_name, [])
        row_id = data.get("ROWID") or f"MOCK-{self.table_name[:4].upper()}-{len(rows)+1:03d}"
        now = _now_iso()
        row = {
            "ROWID": row_id,
            "CREATEDTIME": now,
            "MODIFIEDTIME": now,
        }
        row.update({k: v for k, v in data.items() if k not in ("ROWID", "CREATEDTIME", "MODIFIEDTIME")})
        rows.append(row)
        return row

    def update_row(self, data: Dict[str, Any]) -> Dict[str, Any]:
        rows = _MOCK_DATA.get(self.table_name, [])
        row_id = data.get("ROWID")
        for i, r in enumerate(rows):
            if r.get("ROWID") == row_id:
                updated = dict(r)
                updated.update({k: v for k, v in data.items() if k not in ("ROWID",)})
                updated["MODIFIEDTIME"] = _now_iso()
                rows[i] = updated
                return updated
        return data

    def get_row(self, row_id: str) -> Optional[Dict[str, Any]]:
        for r in _MOCK_DATA.get(self.table_name, []):
            if r.get("ROWID") == row_id:
                return dict(r)
        return None

    def delete_row(self, row_id: str) -> bool:
        rows = _MOCK_DATA.get(self.table_name, [])
        for i, r in enumerate(rows):
            if r.get("ROWID") == row_id:
                rows.pop(i)
                return True
        return False

    def find_all(self, limit: int = 0, offset: int = 0) -> List[Dict[str, Any]]:
        rows = list(_MOCK_DATA.get(self.table_name, []))
        if limit > 0 and offset > 0:
            rows = rows[offset:offset + limit]
        elif limit > 0:
            rows = rows[:limit]
        elif offset > 0:
            rows = rows[offset:]
        return rows

    def find_filtered(
        self,
        limit: int = 100,
        offset: int = 0,
        district_id: Optional[str] = None,
        station_id: Optional[str] = None,
        crime_type: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        keyword: Optional[str] = None,
        sort_by: str = "CREATEDTIME",
        sort_order: str = "DESC",
    ) -> List[Dict[str, Any]]:
        rows = list(_MOCK_DATA.get(self.table_name, []))
        if keyword:
            k = keyword.lower()
            rows = [r for r in rows if k in str(r.get("title", "")).lower() or k in str(r.get("description", "")).lower() or k in str(r.get("crime_type", "")).lower()]
        if district_id:
            rows = [r for r in rows if r.get("district_id") == district_id]
        if station_id:
            rows = [r for r in rows if r.get("station_id") == station_id]
        if crime_type:
            rows = [r for r in rows if r.get("crime_type") == crime_type]
        if status:
            rows = [r for r in rows if r.get("status") == status]
        if date_from:
            rows = [r for r in rows if r.get("CREATEDTIME", "") >= date_from]
        if date_to:
            rows = [r for r in rows if r.get("CREATEDTIME", "") <= date_to]
        reverse = sort_order.upper() == "DESC"
        rows.sort(key=lambda r: r.get(sort_by, ""), reverse=reverse)
        if offset > 0:
            rows = rows[offset:offset + limit]
        else:
            rows = rows[:limit]
        return rows

    def count_by_district(self, district_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
        rows = list(_MOCK_DATA.get(self.table_name, []))
        rows = [r for r in rows if r.get("district_id") == district_id]
        if date_from:
            rows = [r for r in rows if r.get("CREATEDTIME", "") >= date_from]
        if date_to:
            rows = [r for r in rows if r.get("CREATEDTIME", "") <= date_to]
        return len(rows)

    def count_by_station(self, station_id: str, date_from: Optional[str] = None, date_to: Optional[str] = None) -> int:
        rows = list(_MOCK_DATA.get(self.table_name, []))
        rows = [r for r in rows if r.get("station_id") == station_id]
        if date_from:
            rows = [r for r in rows if r.get("CREATEDTIME", "") >= date_from]
        if date_to:
            rows = [r for r in rows if r.get("CREATEDTIME", "") <= date_to]
        return len(rows)

    def find_active(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        rows = [r for r in _MOCK_DATA.get(self.table_name, []) if r.get("status") in ("active", "open", "under-investigation")]
        if offset > 0:
            rows = rows[offset:offset + limit]
        else:
            rows = rows[:limit]
        return rows

    def search(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        k = search_term.lower()
        rows = [r for r in _MOCK_DATA.get(self.table_name, []) if k in str(r.get("name", "")).lower() or k in str(r.get("title", "")).lower() or k in str(r.get("title", "")).lower()]
        return rows[:limit]

    def count_by_status(self, status: str) -> int:
        return sum(1 for r in _MOCK_DATA.get(self.table_name, []) if r.get("status") == status.upper() or r.get("status") == status)


class MockDatastore:
    def table(self, table_name: str) -> MockTable:
        return MockTable(table_name)


class MockZCQL:
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        q = query.strip()
        upper = q.upper()

        table_match = re.search(r"FROM\s+([A-Za-z_][A-Za-z0-9_]*)", q, re.IGNORECASE)
        if not table_match:
            return []
        table_name = table_match.group(1).strip()

        if upper.startswith("SELECT COUNT("):
            table = MockTable(table_name)
            return [{table_name: {"COUNT(ROWID)": len(table.find_all())}}]

        table = MockTable(table_name)
        rows = table.find_all(limit=1000000, offset=0)

        where_match = re.search(r"\bWHERE\b(.*?)(?:\bORDER\b|\bLIMIT\b|$)", q, re.IGNORECASE | re.DOTALL)
        where_clause = ""
        if where_match:
            where_clause = where_match.group(1).strip()

        if where_clause:
            rows = _apply_where(rows, where_clause)

        order_match = re.search(r"\bORDER\s+BY\s+(\w+)(?:\s+(ASC|DESC))?",
                                q, re.IGNORECASE | re.DOTALL)
        if order_match:
            sort_by = order_match.group(1)
            sort_order = (order_match.group(2) or "DESC").upper()
            rows.sort(key=lambda r: r.get(sort_by, ""), reverse=(sort_order == "DESC"))

        limit_match = re.search(r"\bLIMIT\s+(\d+)(?:\s*,\s*(\d+))?", q, re.IGNORECASE | re.DOTALL)
        if limit_match:
            offset_val = int(limit_match.group(1))
            count = limit_match.group(2)
            if count:
                rows = rows[offset_val:int(count)]
            else:
                rows = rows[:offset_val]

        return [{table_name: r} for r in rows]


def _apply_where(rows: List[Dict[str, Any]], where_clause: str) -> List[Dict[str, Any]]:
    clause = where_clause.strip()
    if clause.startswith("(") and clause.endswith(")"):
        clause = clause[1:-1].strip()
    conditions = re.split(r"\bAND\b", clause, flags=re.IGNORECASE)
    filtered: List[Dict[str, Any]] = []
    for row in rows:
        if all(_eval_condition(row, c.strip()) for c in conditions):
            filtered.append(row)
    return filtered


def _eval_condition(row: Dict[str, Any], condition: str) -> bool:
    condition = condition.strip()
    if not condition:
        return True

    rowid_match = re.search(r"ROWID\s*=\s*'([^']+)'", condition, re.IGNORECASE | re.DOTALL)
    if rowid_match:
        return row.get("ROWID") == rowid_match.group(1)

    like_match = re.search(
        r"(\w+)\s+LIKE\s+'([^']+)'",
        condition,
        re.IGNORECASE | re.DOTALL,
    )
    if like_match:
        col = like_match.group(1)
        pattern = like_match.group(2)
        regex = "^"
        for ch in pattern:
            if ch == "%":
                regex += ".*"
            elif ch == "_":
                regex += "."
            else:
                regex += re.escape(ch)
        regex += "$"
        return bool(re.search(regex, str(row.get(col, "")), re.IGNORECASE))

    comp = re.search(
        r"(\w+)\s*(>=|<=|!=|>|<|=)\s*'([^']*)'",
        condition,
        re.IGNORECASE | re.DOTALL,
    )
    if comp:
        col = comp.group(1)
        op = comp.group(2)
        val = comp.group(3)
        actual = row.get(col)
        if actual is None:
            return False
        try:
            if op == "=":
                return str(actual).lower() == val.lower()
            if op == "!=":
                return str(actual).lower() != val.lower()
            if op == ">":
                return str(actual).lower() > val.lower()
            if op == ">=":
                return str(actual).lower() >= val.lower()
            if op == "<":
                return str(actual).lower() < val.lower()
            if op == "<=":
                return str(actual).lower() <= val.lower()
        except Exception:
            return False
        return True

    return True


class MockApp:
    def datastore(self) -> MockDatastore:
        return MockDatastore()

    def zcql(self) -> MockZCQL:
        return MockZCQL()


_mock_app = MockApp()


def get_mock_app() -> MockApp:
    return _mock_app
