from typing import List, Dict, Any, Optional
from fastapi import Request
from app.repositories.base_repository import BaseCatalystRepository
from app.core.exceptions import RepositoryError
from zcatalyst_sdk.exceptions import CatalystError
from app.core.logger import logger

class NetworkRepository(BaseCatalystRepository):
    """
    Repository for network graph aggregations backed by Catalyst Data Store.
    """

    def __init__(self, request: Request):
        super().__init__(request, table_name="Crime")

    async def get_network_data(self, limit: int = 500) -> Dict[str, Any]:
        """Retrieves raw data for network graph construction."""
        try:
            crimes = await self._fetch_crimes(limit)
            firs = await self._fetch_firs(limit)
            criminals = await self._fetch_criminals(limit)
            districts = await self._fetch_districts(limit)
            stations = await self._fetch_stations(limit)
            officers = await self._fetch_officers(limit)
            return {
                "crimes": crimes,
                "firs": firs,
                "criminals": criminals,
                "districts": districts,
                "stations": stations,
                "officers": officers,
            }
        except CatalystError as e:
            logger.error(f"Error fetching network data: {e}")
            raise RepositoryError(f"Failed to fetch network data: {e}")

    async def _fetch_crimes(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM Crime LIMIT {limit}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "Crime" in item:
                rows.append(item["Crime"])
        return rows

    async def _fetch_firs(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM FIR LIMIT {limit}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "FIR" in item:
                rows.append(item["FIR"])
        return rows

    async def _fetch_criminals(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM Criminal LIMIT {limit}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "Criminal" in item:
                rows.append(item["Criminal"])
        return rows

    async def _fetch_districts(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM District LIMIT {limit}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "District" in item:
                rows.append(item["District"])
        return rows

    async def _fetch_stations(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM PoliceStation LIMIT {limit}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "PoliceStation" in item:
                rows.append(item["PoliceStation"])
        return rows

    async def _fetch_officers(self, limit: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM Officer LIMIT {limit}"
        result = self.zcql.execute_query(query)
        rows = []
        for item in result:
            if "Officer" in item:
                rows.append(item["Officer"])
        return rows

    async def find_all_nodes(self, limit: int = 500) -> List[Dict[str, Any]]:
        """Retrieves network nodes as plain dicts for search and reporting."""
        data = await self.get_network_data(limit=limit)
        nodes: List[Dict[str, Any]] = []

        for criminal in data.get("criminals", []):
            cid = criminal.get("ROWID", criminal.get("id", ""))
            nodes.append({
                "id": cid,
                "label": criminal.get("name", "Unknown"),
                "node_type": "Offender",
                "properties": criminal,
            })

        for crime in data.get("crimes", []):
            cid = crime.get("ROWID", "")
            nodes.append({
                "id": cid,
                "label": crime.get("title", "Unknown Crime"),
                "node_type": "Crime",
                "properties": crime,
            })

        for fir in data.get("firs", []):
            fid = fir.get("ROWID", fir.get("fir_number", ""))
            nodes.append({
                "id": fid,
                "label": f"FIR {fir.get('fir_number', '')}",
                "node_type": "FIR",
                "properties": fir,
            })

        for district in data.get("districts", []):
            did = district.get("ROWID", district.get("id", ""))
            nodes.append({
                "id": did,
                "label": district.get("name", "Unknown District"),
                "node_type": "District",
                "properties": district,
            })

        for station in data.get("stations", []):
            sid = station.get("ROWID", station.get("id", ""))
            nodes.append({
                "id": sid,
                "label": station.get("name", "Unknown Station"),
                "node_type": "PoliceStation",
                "properties": station,
            })

        for officer in data.get("officers", []):
            oid = officer.get("ROWID", officer.get("id", ""))
            nodes.append({
                "id": oid,
                "label": officer.get("name", "Unknown Officer"),
                "node_type": "Officer",
                "properties": officer,
            })

        return nodes[:limit]

    async def find_all_edges(self, limit: int = 500) -> List[Dict[str, Any]]:
        """Retrieves network edges as plain dicts for search and reporting."""
        data = await self.get_network_data(limit=limit)
        edges: List[Dict[str, Any]] = []

        for crime in data.get("crimes", []):
            cid = crime.get("ROWID", "")
            did = crime.get("district_id", "")
            sid = crime.get("station_id", "")
            if did:
                edges.append({"source": cid, "target": did, "type": "occurred_at", "properties": {}})
            if sid:
                edges.append({"source": cid, "target": sid, "type": "investigated_by", "properties": {}})

        for fir in data.get("firs", []):
            fid = fir.get("ROWID", fir.get("fir_number", ""))
            cid = fir.get("crime_id", "")
            sid = fir.get("station_id", "")
            oid = fir.get("officer_id", "")
            if cid:
                edges.append({"source": fid, "target": cid, "type": "registered_in", "properties": {}})
            if sid:
                edges.append({"source": fid, "target": sid, "type": "registered_in", "properties": {}})
            if oid:
                edges.append({"source": fid, "target": oid, "type": "investigated_by", "properties": {}})

        for station in data.get("stations", []):
            sid = station.get("ROWID", station.get("id", ""))
            did = station.get("district_id", "")
            if did:
                edges.append({"source": sid, "target": did, "type": "belongs_to", "properties": {}})

        for officer in data.get("officers", []):
            oid = officer.get("ROWID", officer.get("id", ""))
            sid = officer.get("police_station_id", "")
            if sid:
                edges.append({"source": oid, "target": sid, "type": "belongs_to", "properties": {}})

        return edges[:limit]
