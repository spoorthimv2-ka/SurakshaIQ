from typing import Any, Dict, List, Optional
from collections import defaultdict
from datetime import datetime, timezone
from fastapi import Request

from app.repositories.network_repo import NetworkRepository
from app.repositories.crime_repo import CrimeRepository
from app.repositories.fir_repo import FIRRepository
from app.repositories.district_repo import DistrictRepository
from app.repositories.police_station_repo import PoliceStationRepository
from app.repositories.officer_repo import OfficerRepository
from app.repositories.criminal_repo import CriminalRepository
from app.repositories.prediction_ledger_repo import PredictionLedgerRepository
from app.core.logger import logger
from app.schemas.network import (
    NetworkNode,
    NetworkEdge,
    NetworkStatistics,
    NetworkGraphResponse,
    NetworkSearchResponse,
)


class NetworkService:
    """Service layer for network analysis."""

    def __init__(self, request: Request):
        self.request = request
        self.repo = NetworkRepository(request)
        self.crime_repo = CrimeRepository(request)
        self.fir_repo = FIRRepository(request)
        self.district_repo = DistrictRepository(request)
        self.station_repo = PoliceStationRepository(request)
        self.officer_repo = OfficerRepository(request)
        self.criminal_repo = CriminalRepository(request)

    async def _record_ledger(self, entity_type: str, entity_id: str, score: float, level: str) -> None:
        try:
            repo = PredictionLedgerRepository(self.request)
            await repo.record({
                "entity_type": entity_type,
                "entity_id": entity_id,
                "entity_name": entity_id,
                "prediction_type": "NETWORK",
                "score": score,
                "level": level,
                "factors": [],
                "model_version": "v1-heuristic",
                "scored_at": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as e:
            logger.warning(f"Ledger write failed: {e}")

    async def get_network(self, officer: Dict[str, Any], limit: int = 500) -> NetworkGraphResponse:
        """Builds the full relationship graph from Catalyst Data Store."""
        
        data = await self.repo.get_network_data(limit=limit)
        return self._build_graph(data)

    async def get_statistics(self, officer: Dict[str, Any]) -> NetworkStatistics:
        """Returns network statistics."""
        
        data = await self.repo.get_network_data(limit=1000)
        graph = self._build_graph(data)
        node_types = defaultdict(int)
        for node in graph.nodes:
            node_types[node.type] += 1

        degree: Dict[str, int] = defaultdict(int)
        for edge in graph.edges:
            degree[edge.source] += 1
            degree[edge.target] += 1

        avg_connections = sum(degree.values()) / max(len(graph.nodes), 1)
        stats = NetworkStatistics(
            total_nodes=len(graph.nodes),
            total_edges=len(graph.edges),
            connected_offenders=node_types.get("Offender", 0),
            connected_stations=node_types.get("PoliceStation", 0),
            connected_districts=node_types.get("District", 0),
            average_connections=round(avg_connections, 2),
        )
        await self._record_ledger("NetworkGraph", "full", round(avg_connections, 2), "LOW")
        return stats

    async def get_offender_network(self, officer: Dict[str, Any], offender_id: str) -> NetworkGraphResponse:
        """Returns graph data for a specific offender."""
        
        data = await self.repo.get_network_data(limit=1000)
        graph = self._build_graph(data)
        connected_ids = {offender_id}
        for edge in graph.edges:
            if edge.source == offender_id:
                connected_ids.add(edge.target)
            if edge.target == offender_id:
                connected_ids.add(edge.source)

        filtered_nodes = [n for n in graph.nodes if n.id in connected_ids]
        filtered_edges = [e for e in graph.edges if e.source in connected_ids and e.target in connected_ids]
        return NetworkGraphResponse(
            nodes=filtered_nodes,
            edges=filtered_edges,
            statistics=graph.statistics,
            metadata=graph.metadata,
        )

    async def get_station_network(self, officer: Dict[str, Any], station_id: str) -> NetworkGraphResponse:
        """Returns graph data for a specific police station."""
        
        data = await self.repo.get_network_data(limit=1000)
        graph = self._build_graph(data)
        connected_ids = {station_id}
        for edge in graph.edges:
            if edge.source == station_id:
                connected_ids.add(edge.target)
            if edge.target == station_id:
                connected_ids.add(edge.source)

        filtered_nodes = [n for n in graph.nodes if n.id in connected_ids]
        filtered_edges = [e for e in graph.edges if e.source in connected_ids and e.target in connected_ids]
        return NetworkGraphResponse(
            nodes=filtered_nodes,
            edges=filtered_edges,
            statistics=graph.statistics,
            metadata=graph.metadata,
        )

    async def get_district_network(self, officer: Dict[str, Any], district_id: str) -> NetworkGraphResponse:
        """Returns graph data for a specific district."""
        
        data = await self.repo.get_network_data(limit=1000)
        graph = self._build_graph(data)
        connected_ids = {district_id}
        for edge in graph.edges:
            if edge.source == district_id:
                connected_ids.add(edge.target)
            if edge.target == district_id:
                connected_ids.add(edge.source)

        filtered_nodes = [n for n in graph.nodes if n.id in connected_ids]
        filtered_edges = [e for e in graph.edges if e.source in connected_ids and e.target in connected_ids]
        return NetworkGraphResponse(
            nodes=filtered_nodes,
            edges=filtered_edges,
            statistics=graph.statistics,
            metadata=graph.metadata,
        )

    async def search(self, officer: Dict[str, Any], query: str, limit: int = 50) -> NetworkSearchResponse:
        """Searches the network graph."""
        
        if not query:
            raise ValueError("Query parameter is required")

        data = await self.repo.get_network_data(limit=1000)
        graph = self._build_graph(data)
        query_lower = query.lower()
        matched_nodes = [
            n for n in graph.nodes
            if query_lower in n.label.lower() or query_lower in n.type.lower() or any(query_lower in str(v).lower() for v in n.properties.values())
        ]
        matched_ids = {n.id for n in matched_nodes}
        matched_edges = [e for e in graph.edges if e.source in matched_ids or e.target in matched_ids]
        return NetworkSearchResponse(query=query, nodes=matched_nodes, edges=matched_edges)

    def _build_graph(self, data: Dict[str, Any]) -> NetworkGraphResponse:
        """Constructs the network graph from raw data."""
        nodes: List[NetworkNode] = []
        edges: List[NetworkEdge] = []
        node_ids = set()

        def add_node(node_id: str, label: str, node_type: str, properties: Dict[str, Any] = None) -> str:
            if node_id not in node_ids:
                nodes.append(NetworkNode(id=node_id, label=label, type=node_type, properties=properties or {}))
                node_ids.add(node_id)
            return node_id

        for criminal in data.get("criminals", []):
            cid = criminal.get("ROWID", criminal.get("id", ""))
            add_node(cid, criminal.get("name", "Unknown"), "Offender", criminal)

        for crime in data.get("crimes", []):
            crime_id = crime.get("ROWID", "")
            add_node(crime_id, crime.get("title", "Unknown Crime"), "Crime", crime)

            district_id = crime.get("district_id", "")
            station_id = crime.get("station_id", "")

            if district_id:
                add_node(district_id, f"District {district_id}", "District")
                edges.append(NetworkEdge(source=crime_id, target=district_id, type="occurred_at", properties={}))

            if station_id:
                add_node(station_id, f"Station {station_id}", "PoliceStation")
                edges.append(NetworkEdge(source=crime_id, target=station_id, type="investigated_by", properties={}))

        for fir in data.get("firs", []):
            fir_id = fir.get("ROWID", fir.get("fir_number", ""))
            add_node(fir_id, f"FIR {fir.get('fir_number', '')}", "FIR", fir)

            crime_id = fir.get("crime_id", "")
            if crime_id and any(n.id == crime_id for n in nodes):
                edges.append(NetworkEdge(source=fir_id, target=crime_id, type="registered_in", properties={}))

            station_id = fir.get("station_id", "")
            if station_id:
                add_node(station_id, f"Station {station_id}", "PoliceStation")
                edges.append(NetworkEdge(source=fir_id, target=station_id, type="registered_in", properties={}))

            officer_id = fir.get("officer_id", "")
            if officer_id:
                add_node(officer_id, f"Officer {officer_id}", "Officer")
                edges.append(NetworkEdge(source=fir_id, target=officer_id, type="investigated_by", properties={}))

        for district in data.get("districts", []):
            did = district.get("ROWID", district.get("id", ""))
            add_node(did, district.get("name", "Unknown District"), "District", district)

        for station in data.get("stations", []):
            sid = station.get("ROWID", station.get("id", ""))
            add_node(sid, station.get("name", "Unknown Station"), "PoliceStation", station)
            district_id = station.get("district_id", "")
            if district_id:
                edges.append(NetworkEdge(source=sid, target=district_id, type="belongs_to", properties={}))

        for officer in data.get("officers", []):
            oid = officer.get("ROWID", officer.get("id", ""))
            add_node(oid, officer.get("name", "Unknown Officer"), "Officer", officer)
            station_id = officer.get("police_station_id", "")
            if station_id:
                edges.append(NetworkEdge(source=oid, target=station_id, type="belongs_to", properties={}))

        node_types = defaultdict(int)
        for node in nodes:
            node_types[node.type] += 1
        total_nodes = len(nodes)
        total_edges = len(edges)
        avg_connections = (total_edges * 2) / max(total_nodes, 1)

        statistics = NetworkStatistics(
            total_nodes=total_nodes,
            total_edges=total_edges,
            connected_offenders=node_types.get("Offender", 0),
            connected_stations=node_types.get("PoliceStation", 0),
            connected_districts=node_types.get("District", 0),
            average_connections=round(avg_connections, 2),
        )

        return NetworkGraphResponse(
            nodes=nodes,
            edges=edges,
            statistics=statistics,
            metadata={"source": "catalyst_datastore"},
        )
