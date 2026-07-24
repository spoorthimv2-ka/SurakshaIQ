"""
Minimal demo seed for SurakshaIQ Catalyst tables.

Creates base data so hotspots, repeat-offenders, network, risk, and
anomaly panels return non-empty results.  Optionally inserts one
pre-computed CrimeHotspotCluster row so the clustering cache has data.

Also creates a known demo officer account for local login:
    email:    demo@karnatakapolice.gov.in
    password: Demo@1234

Run inside Catalyst AppSail, or locally with CATALYST_* env vars set:
    python scripts/seed_demo.py
"""
import asyncio
import os
from datetime import datetime, timezone, timedelta

from zcatalyst_sdk import initialize_app
import bcrypt


DEMO_EMAIL = "demo@karnatakapolice.gov.in"
DEMO_PASSWORD = "Demo@1234"
DEMO_ROLE = "SYSTEM_ADMINISTRATOR"


async def main() -> None:
    app = initialize_app()
    ds = app.datastore()
    now = datetime.now(timezone.utc)

    # --- Districts --------------------------------------------------------
    d1 = ds.table("District").insert_row({
        "name": "Central District", "state": "Karnataka", "status": "ACTIVE",
    })
    d2 = ds.table("District").insert_row({
        "name": "North District", "state": "Karnataka", "status": "ACTIVE",
    })

    # --- Police Stations --------------------------------------------------
    s1 = ds.table("PoliceStation").insert_row({
        "name": "Central PS", "district_id": d1["ROWID"], "status": "ACTIVE",
    })
    s2 = ds.table("PoliceStation").insert_row({
        "name": "North PS", "district_id": d2["ROWID"], "status": "ACTIVE",
    })

    # --- Demo Officer (idempotent) -----------------------------------------
    existing = ds.table("Officer").execute_query(
        f"SELECT ROWID FROM Officer WHERE email = '{DEMO_EMAIL}' LIMIT 1"
    )
    officer_rowid = None
    if existing and "Officer" in existing[0]:
        officer_rowid = existing[0]["Officer"].get("ROWID")

    if not officer_rowid:
        hashed = bcrypt.hashpw(DEMO_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        officer = ds.table("Officer").insert_row({
            "name": "Demo Officer",
            "email": DEMO_EMAIL,
            "role": DEMO_ROLE,
            "hashed_password": hashed,
            "police_station_id": s1["ROWID"],
            "status": "ACTIVE",
        })
        officer_rowid = officer["ROWID"]
        print(f"Created demo officer: {DEMO_EMAIL}")
    else:
        print(f"Demo officer already exists: {DEMO_EMAIL}")

    # --- Crimes (5) -------------------------------------------------------
    crime_specs = [
        ("THEFT",     d1["ROWID"], s1["ROWID"], -12.0),
        ("THEFT",     d1["ROWID"], s1["ROWID"], -11.0),
        ("ASSAULT",   d1["ROWID"], s1["ROWID"], -10.0),
        ("ROBBERY",   d2["ROWID"], s2["ROWID"],  -9.0),
        ("ASSAULT",   d2["ROWID"], s2["ROWID"],  -8.0),
    ]
    crimes = []
    for ctype, did, sid, lat_offset in crime_specs:
        crime = ds.table("Crime").insert_row({
            "title": f"Demo {ctype} #{len(crimes)+1}",
            "crime_type": ctype,
            "description": "Seeded for demo",
            "district_id": did,
            "station_id": sid,
            "status": "ACTIVE",
            "latitude": 12.97 + lat_offset * 0.01,
            "longitude": 77.59 + lat_offset * 0.01,
            "address": f"Seed address {len(crimes)+1}",
        })
        crimes.append(crime)

    # --- Criminals (3) ----------------------------------------------------
    criminals = []
    for i in range(3):
        criminal = ds.table("Criminal").insert_row({
            "name": f"Demo Criminal {i+1}",
            "alias": f"Alias {i+1}",
            "risk_level": "HIGH" if i == 0 else "MEDIUM",
            "status": "ACTIVE",
            "last_known_location": "Central District" if i < 2 else "North District",
        })
        criminals.append(criminal)

    # --- CrimeCriminalLinks (explicit) ------------------------------------
    links_created = 0
    for crime in crimes[:3]:
        ds.table("CrimeCriminalLink").insert_row({
            "crime_id": crime["ROWID"],
            "criminal_id": criminals[0]["ROWID"],
            "role": "ACCUSED",
        })
        links_created += 1
    for crime in crimes[3:]:
        ds.table("CrimeCriminalLink").insert_row({
            "crime_id": crime["ROWID"],
            "criminal_id": criminals[1]["ROWID"],
            "role": "ACCUSED",
        })
        links_created += 1

    # --- FIRs (3) ---------------------------------------------------------
    for i, crime in enumerate(crimes[:3]):
        ds.table("FIR").insert_row({
            "fir_number": f"FIR-DEMO-{i+1:03d}",
            "crime_id": crime["ROWID"],
            "district_id": crime["district_id"],
            "station_id": crime["station_id"],
            "officer_id": officer_rowid,
            "status": "ACTIVE",
            "description": "Seeded FIR",
        })

    # --- Alerts (2) -------------------------------------------------------
    ds.table("Alert").insert_row({
        "type": "CRIME_SPIKE",
        "severity": "HIGH",
        "status": "ACTIVE",
        "message": "Demo alert: unusual theft spike in Central District",
        "district_id": d1["ROWID"],
    })
    ds.table("Alert").insert_row({
        "type": "ANOMALY",
        "severity": "MEDIUM",
        "status": "ACTIVE",
        "message": "Demo alert: repeat offender activity detected in North PS",
        "district_id": d2["ROWID"],
    })

    # --- Optional: pre-computed hotspot cluster ---------------------------
    try:
        ds.table("CrimeHotspotCluster").insert_row({
            "cluster_id": "CLUSTER-DEMO-1",
            "district_id": d1["ROWID"],
            "station_id": s1["ROWID"],
            "center_lat": 12.9698,
            "center_lon": 77.5900,
            "radius_m": 1200.0,
            "crime_count": 3,
            "period_start": (now - timedelta(days=30)).isoformat(),
            "period_end": now.isoformat(),
            "scored_at": now.isoformat(),
        })
    except Exception as exc:
        print(f"Cluster seed skipped (table may not exist yet): {exc}")

    # --- Optional: sample prediction ledger entry -------------------------
    try:
        ds.table("PredictionLedger").insert_row({
            "entity_type": "District",
            "entity_id": d1["ROWID"],
            "entity_name": "Central District",
            "prediction_type": "RISK",
            "score": 45.5,
            "level": "MEDIUM",
            "factors": [],
            "model_version": "v1-seed",
            "scored_at": now.isoformat(),
        })
    except Exception as exc:
        print(f"Ledger seed skipped (table may not exist yet): {exc}")

    print(
        f"Seeded: {len(crimes)} crimes, {len(criminals)} criminals, "
        f"{links_created} links, 3 FIRs, 2 alerts, 2 districts, 2 stations, 1 officer"
    )
    print(f"Demo login: {DEMO_EMAIL} / {DEMO_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
