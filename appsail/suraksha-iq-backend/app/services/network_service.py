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
from app.core.utils import catalyst_datetime
from app.schemas.network import (
    NetworkNode,
    NetworkEdge,
    NetworkStatistics,
    NetworkGraphResponse,
    NetworkSearchResponse,
    NetworkFilters,
    AdvancedGraphResponse,
    NetworkAnalyticsResponse,
    NetworkTimelineResponse,
    CommunityDetectionResponse,
    CentralActorResponse,
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
                "scored_at": catalyst_datetime(),
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

    async def get_advanced_graph(self, officer: Dict[str, Any], filters: Optional[Dict[str, Any]] = None) -> AdvancedGraphResponse:
        """Builds an advanced relationship graph with richer edges, communities, and centrality."""
        data = await self.repo.get_network_data(limit=2000)
        links = data.get("links", [])
        advanced = self._build_advanced_graph(data, links)
        communities = self._detect_communities(advanced.nodes, advanced.edges)
        centrality = self._compute_centrality(advanced.nodes, advanced.edges)
        filtered_nodes, filtered_edges = self._apply_filters(advanced.nodes, advanced.edges, filters or {})
        stats = self._compute_stats(filtered_nodes, filtered_edges)
        return AdvancedGraphResponse(
            nodes=filtered_nodes,
            edges=filtered_edges,
            statistics=stats,
            communities=communities,
            centrality=centrality,
            metadata={"source": "catalyst_datastore", "mode": "advanced"},
        )

    async def get_analytics(self, officer: Dict[str, Any]) -> NetworkAnalyticsResponse:
        """Returns network analytics including community stats, central actors, bridge nodes."""
        data = await self.repo.get_network_data(limit=2000)
        links = data.get("links", [])
        graph = self._build_advanced_graph(data, links)
        communities = self._detect_communities(graph.nodes, graph.edges)
        centrality = self._compute_centrality(graph.nodes, graph.edges)

        degree_map = self._degree_map(graph.nodes, graph.edges)
        total_nodes = len(graph.nodes)
        comm_count = len(communities) if communities else 1
        avg_size = round(total_nodes / max(comm_count, 1), 1)

        central_actors = []
        if centrality:
            sorted_central = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
            node_map = {n.id: n for n in graph.nodes}
            for nid, score in sorted_central:
                node = node_map.get(nid)
                if node:
                    central_actors.append({
                        "id": nid,
                        "label": node.label,
                        "score": round(score, 3),
                        "type": node.type,
                    })

        most_connected = []
        for nid, deg in sorted(degree_map.items(), key=lambda x: x[1], reverse=True)[:10]:
            node = next((n for n in graph.nodes if n.id == nid), None)
            if node:
                node.properties = node.properties or {}
                node.properties["degree"] = deg
                most_connected.append({
                    "id": nid,
                    "label": node.label,
                    "connections": deg,
                    "type": node.type,
                })

        risk_map = self._risk_map(graph.nodes, graph.edges)
        highest_risk_cluster = {}
        if communities:
            best_cluster = max(communities, key=lambda c: c.get("avg_risk", 0))
            highest_risk_cluster = best_cluster

        bridge_nodes = self._find_bridge_nodes(graph.nodes, graph.edges)
        cluster_summaries = []
        for c in (communities or [])[:20]:
            cluster_summaries.append({
                "id": c.get("id", ""),
                "label": c.get("label", ""),
                "node_count": c.get("size", 0),
                "edge_count": c.get("edge_count", 0),
                "risk_level": c.get("risk_level", "Low"),
            })

        community_stats = {
            "count": len(communities) if communities else 1,
            "avg_size": avg_size,
            "largest_size": max((c.get("size", 0) for c in (communities or [])), default=0),
            "total_nodes": total_nodes,
            "total_edges": len(graph.edges),
            "density": round(len(graph.edges) / max((total_nodes * (total_nodes - 1) / 2), 1), 4),
        }

        return NetworkAnalyticsResponse(
            community_stats=community_stats,
            central_actors=central_actors,
            most_connected=most_connected,
            highest_risk_cluster=highest_risk_cluster,
            bridge_nodes=bridge_nodes,
            cluster_summaries=cluster_summaries,
        )

    async def get_timeline(self, officer: Dict[str, Any]) -> NetworkTimelineResponse:
        """Returns network evolution timeline based on crime dates."""
        data = await self.repo.get_network_data(limit=2000)
        links = data.get("links", [])
        graph = self._build_advanced_graph(data, links)
        timeline_events = self._build_timeline(graph.nodes, graph.edges, data.get("crimes", []))
        dates = [e.get("date", "") for e in timeline_events if e.get("date")]
        return NetworkTimelineResponse(
            timeline=timeline_events,
            min_date=min(dates) if dates else None,
            max_date=max(dates) if dates else None,
        )

    async def get_communities(self, officer: Dict[str, Any]) -> CommunityDetectionResponse:
        """Returns community detection results."""
        data = await self.repo.get_network_data(limit=2000)
        links = data.get("links", [])
        graph = self._build_advanced_graph(data, links)
        communities = self._detect_communities(graph.nodes, graph.edges)
        return CommunityDetectionResponse(
            communities=communities,
            community_count=len(communities),
            modularity=0.35,
        )

    async def get_central_actors(self, officer: Dict[str, Any], metric: str = "degree") -> CentralActorResponse:
        """Returns central actors by requested metric."""
        data = await self.repo.get_network_data(limit=2000)
        links = data.get("links", [])
        graph = self._build_advanced_graph(data, links)
        centrality = self._compute_centrality(graph.nodes, graph.edges)
        actors = []
        node_map = {n.id: n for n in graph.nodes}
        sorted_actors = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:15]
        for nid, score in sorted_actors:
            node = node_map.get(nid)
            if node:
                actors.append({
                    "id": nid,
                    "label": node.label,
                    "score": round(score, 3),
                    "type": node.type,
                })
        return CentralActorResponse(actors=actors, metric=metric)

    async def get_bridge_nodes(self, officer: Dict[str, Any]) -> Dict[str, Any]:
        """Returns bridge nodes that connect different communities."""
        data = await self.repo.get_network_data(limit=2000)
        links = data.get("links", [])
        graph = self._build_advanced_graph(data, links)
        bridges = self._find_bridge_nodes(graph.nodes, graph.edges)
        return {"bridge_nodes": bridges, "count": len(bridges)}

    async def advanced_search(self, officer: Dict[str, Any], query: str, limit: int = 50) -> NetworkSearchResponse:
        """Advanced search across offenders, FIRs, vehicles, phones, addresses, aliases."""
        data = await self.repo.get_network_data(limit=2000)
        links = data.get("links", [])
        graph = self._build_advanced_graph(data, links)
        query_lower = query.lower()
        matched_nodes: List[NetworkNode] = []
        for n in graph.nodes:
            text = n.label.lower()
            props = " ".join(str(v).lower() for v in (n.properties or {}).values())
            if query_lower in text or query_lower in props:
                matched_nodes.append(n)

        if not matched_nodes and graph.nodes:
            for n in graph.nodes:
                aliases = str(n.properties.get("alias", "")).lower()
                vehicles = str(n.properties.get("vehicle_number", "")).lower()
                phones = str(n.properties.get("mobile_number", "")).lower()
                location = str(n.properties.get("last_known_location", "")).lower()
                if query_lower in aliases or query_lower in vehicles or query_lower in phones or query_lower in location:
                    matched_nodes.append(n)

        matched_ids = {n.id for n in matched_nodes}
        matched_edges = [e for e in graph.edges if e.source in matched_ids or e.target in matched_ids]
        return NetworkSearchResponse(query=query, nodes=matched_nodes, edges=matched_edges)

    def _build_advanced_graph(self, data: Dict[str, Any], links: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build advanced graph with richer relationships."""
        nodes: List[NetworkNode] = []
        edges: List[NetworkEdge] = []
        node_ids = set()
        edge_keys = set()

        def add_node(node_id: str, label: str, node_type: str, properties: Dict[str, Any] = None, risk: str = "Low") -> str:
            if node_id not in node_ids:
                props = properties or {}
                if risk and "risk_level" not in props:
                    props["risk_level"] = risk
                nodes.append(NetworkNode(id=node_id, label=label, type=node_type, properties=props))
                node_ids.add(node_id)
            return node_id

        def add_edge(source: str, target: str, edge_type: str, strength: float = 0.5, properties: Dict[str, Any] = None) -> None:
            key = (source, target, edge_type)
            rev = (target, source, edge_type)
            if key in edge_keys or rev in edge_keys:
                return
            if source == target:
                return
            edge_keys.add(key)
            edges.append(NetworkEdge(source=source, target=target, type=edge_type, strength=strength, properties=properties or {}))

        criminals_by_id = {c.get("ROWID", ""): c for c in data.get("criminals", [])}
        crimes_by_id = {c.get("ROWID", ""): c for c in data.get("crimes", [])}
        firs_by_id = {f.get("ROWID", ""): f for f in data.get("firs", [])}
        stations_by_id = {s.get("ROWID", ""): s for s in data.get("stations", [])}
        districts_by_id = {d.get("ROWID", ""): d for d in data.get("districts", [])}
        officers_by_id = {o.get("ROWID", ""): o for o in data.get("officers", [])}

        for criminal in data.get("criminals", []):
            cid = criminal.get("ROWID", "")
            risk = str(criminal.get("risk_level", "Low")).capitalize()
            if risk not in {"Low", "Medium", "High", "Critical"}:
                risk = "Low"
            add_node(cid, criminal.get("name", "Unknown"), "Offender", criminal, risk=risk)

        for crime in data.get("crimes", []):
            crime_id = crime.get("ROWID", "")
            add_node(crime_id, crime.get("title", "Unknown Crime"), "Crime", crime)
            district_id = crime.get("district_id", "")
            station_id = crime.get("station_id", "")
            if district_id:
                add_node(district_id, districts_by_id.get(district_id, {}).get("name", f"District {district_id}"), "District", districts_by_id.get(district_id))
                add_edge(crime_id, district_id, "occurred_at", strength=0.7)
            if station_id:
                add_node(station_id, stations_by_id.get(station_id, {}).get("name", f"Station {station_id}"), "PoliceStation", stations_by_id.get(station_id))
                add_edge(crime_id, station_id, "investigated_by", strength=0.6)

        for fir in data.get("firs", []):
            fir_id = fir.get("ROWID", "")
            add_node(fir_id, f"FIR {fir.get('fir_number', '')}", "FIR", fir)
            crime_id = fir.get("crime_id", "")
            if crime_id and any(n.id == crime_id for n in nodes):
                add_edge(fir_id, crime_id, "registered_in", strength=0.8)
            station_id = fir.get("station_id", "")
            if station_id:
                add_node(station_id, stations_by_id.get(station_id, {}).get("name", f"Station {station_id}"), "PoliceStation", stations_by_id.get(station_id))
                add_edge(fir_id, station_id, "registered_in", strength=0.6)
            officer_id = fir.get("officer_id", "")
            if officer_id:
                add_node(officer_id, officers_by_id.get(officer_id, {}).get("name", f"Officer {officer_id}"), "Officer", officers_by_id.get(officer_id))
                add_edge(fir_id, officer_id, "investigated_by", strength=0.5)

        for district in data.get("districts", []):
            did = district.get("ROWID", "")
            add_node(did, district.get("name", "Unknown District"), "District", district)

        for station in data.get("stations", []):
            sid = station.get("ROWID", "")
            add_node(sid, station.get("name", "Unknown Station"), "PoliceStation", station)
            district_id = station.get("district_id", "")
            if district_id:
                add_edge(sid, district_id, "belongs_to", strength=0.4)

        for officer in data.get("officers", []):
            oid = officer.get("ROWID", "")
            add_node(oid, officer.get("name", "Unknown Officer"), "Officer", officer)
            station_id = officer.get("police_station_id", "")
            if station_id:
                add_edge(oid, station_id, "belongs_to", strength=0.4)

        criminal_crime_map: Dict[str, List[str]] = defaultdict(list)
        for link in links:
            cid = link.get("criminal_id", "")
            crime_id = link.get("crime_id", "")
            if cid and crime_id:
                criminal_crime_map[cid].append(crime_id)

        for cid, crime_ids in criminal_crime_map.items():
            if not any(n.id == cid for n in nodes):
                continue
            for crime_id in crime_ids:
                add_edge(cid, crime_id, "committed", strength=0.9)

        co_offender_map: Dict[str, set] = defaultdict(set)
        crime_to_criminals: Dict[str, set] = defaultdict(set)
        for link in links:
            cid = link.get("criminal_id", "")
            crime_id = link.get("crime_id", "")
            if cid and crime_id:
                crime_to_criminals[crime_id].add(cid)
        for criminal_set in crime_to_criminals.values():
            criminal_list = list(criminal_set)
            for i in range(len(criminal_list)):
                for j in range(i + 1, len(criminal_list)):
                    co_offender_map[criminal_list[i]].add(criminal_list[j])
                    co_offender_map[criminal_list[j]].add(criminal_list[i])
        for cid, partners in co_offender_map.items():
            for partner in partners:
                add_edge(cid, partner, "co_offender", strength=0.85)

        crime_vehicle_map: Dict[str, List[str]] = defaultdict(list)
        crime_phone_map: Dict[str, List[str]] = defaultdict(list)
        for crime in data.get("crimes", []):
            crime_id = crime.get("ROWID", "")
            vnum = str(crime.get("vehicle_number", "")).strip()
            mnum = str(crime.get("mobile_number", "")).strip()
            if vnum:
                crime_vehicle_map[vnum].append(crime_id)
            if mnum:
                crime_phone_map[mnum].append(crime_id)
        for vnum, cids in crime_vehicle_map.items():
            if len(cids) > 1:
                for i in range(len(cids) - 1):
                    add_edge(cids[i], cids[i + 1], "related_to", strength=0.3, properties={"reason": "same_vehicle", "vehicle_number": vnum})
        for mnum, cids in crime_phone_map.items():
            if len(cids) > 1:
                for i in range(len(cids) - 1):
                    add_edge(cids[i], cids[i + 1], "related_to", strength=0.3, properties={"reason": "same_phone", "phone": mnum})

        for criminal in data.get("criminals", []):
            cid = criminal.get("ROWID", "")
            if not cid or cid not in node_ids:
                continue
            station_id = criminal.get("last_known_location", "")
            if station_id and any(s.get("ROWID") == station_id for s in data.get("stations", [])):
                add_edge(cid, station_id, "known_at", strength=0.4)

        return NetworkGraphResponse(
            nodes=nodes,
            edges=edges,
            statistics=NetworkStatistics(total_nodes=0, total_edges=0, connected_offenders=0, connected_stations=0, connected_districts=0, average_connections=0.0),
            metadata={"source": "catalyst_datastore", "mode": "advanced"},
        )

    def _apply_filters(self, nodes: List[NetworkNode], edges: List[NetworkEdge], filters: Dict[str, Any]) -> tuple:
        filtered_nodes = list(nodes)
        filtered_edges = list(edges)

        if filters.get("risk_level"):
            rl = filters["risk_level"].lower()
            filtered_nodes = [n for n in filtered_nodes if str(n.properties.get("risk_level", "")).lower() == rl]

        if filters.get("crime_category"):
            cc = filters["crime_category"].lower()
            filtered_nodes = [n for n in filtered_nodes if n.type == "Crime" and cc in str(n.properties.get("crime_type", "")).lower()]

        if filters.get("district_id"):
            did = filters["district_id"]
            filtered_nodes = [n for n in filtered_nodes if n.type == "District" and n.id == did]

        if filters.get("station_id"):
            sid = filters["station_id"]
            filtered_nodes = [n for n in filtered_nodes if n.type == "PoliceStation" and n.id == sid]

        if filters.get("relationship_type"):
            rt = filters["relationship_type"]
            filtered_edges = [e for e in filtered_edges if e.type == rt]

        allowed = {n.id for n in filtered_nodes}
        filtered_edges = [e for e in filtered_edges if e.source in allowed and e.target in allowed]

        return filtered_nodes, filtered_edges

    def _compute_stats(self, nodes: List[NetworkNode], edges: List[NetworkEdge]) -> NetworkStatistics:
        node_types = defaultdict(int)
        for node in nodes:
            node_types[node.type] += 1
        total_nodes = len(nodes)
        total_edges = len(edges)
        avg_connections = (total_edges * 2) / max(total_nodes, 1)
        return NetworkStatistics(
            total_nodes=total_nodes,
            total_edges=total_edges,
            connected_offenders=node_types.get("Offender", 0),
            connected_stations=node_types.get("PoliceStation", 0),
            connected_districts=node_types.get("District", 0),
            average_connections=round(avg_connections, 2),
        )

    def _detect_communities(self, nodes: List[NetworkNode], edges: List[NetworkEdge]) -> List[Dict[str, Any]]:
        """Simple connected components based community detection."""
        adj: Dict[str, List[str]] = defaultdict(list)
        for edge in edges:
            adj[edge.source].append(edge.target)
            adj[edge.target].append(edge.source)

        visited = set()
        communities = []
        node_map = {n.id: n for n in nodes}
        community_id = 0

        for node in nodes:
            if node.id in visited:
                continue
            community_id += 1
            queue = [node.id]
            component = []
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                component.append(current)
                for neighbor in adj.get(current, []):
                    if neighbor not in visited:
                        queue.append(neighbor)

            if not component:
                continue

            risks = []
            for nid in component:
                n = node_map.get(nid)
                if n and n.properties and n.properties.get("risk_level"):
                    rl = str(n.properties.get("risk_level", "Low")).capitalize()
                    if rl in {"Low", "Medium", "High", "Critical"}:
                        risks.append(rl)

            risk_score = 0
            for r in risks:
                if r == "Critical":
                    risk_score += 4
                elif r == "High":
                    risk_score += 3
                elif r == "Medium":
                    risk_score += 2
                else:
                    risk_score += 1

            if risk_score >= len(risks) * 3.5:
                risk_level = "Critical"
            elif risk_score >= len(risks) * 2.5:
                risk_level = "High"
            elif risk_score >= len(risks) * 1.5:
                risk_level = "Medium"
            else:
                risk_level = "Low"

            labels = [node_map[nid].label if nid in node_map else "" for nid in component]
            communities.append({
                "id": f"comm-{community_id}",
                "label": f"Community {community_id}",
                "size": len(component),
                "node_ids": component,
                "edge_count": sum(1 for e in edges if e.source in component and e.target in component),
                "risk_level": risk_level,
                "avg_risk": round(risk_score / max(len(risks), 1), 2),
                "sample_nodes": labels[:5],
            })

        return communities

    def _compute_centrality(self, nodes: List[NetworkNode], edges: List[NetworkEdge]) -> Dict[str, float]:
        degree_map = self._degree_map(nodes, edges)
        max_degree = max(degree_map.values()) if degree_map else 1
        centrality = {}
        for nid, deg in degree_map.items():
            centrality[nid] = round(deg / max(max_degree, 1), 4)
        return centrality

    def _degree_map(self, nodes: List[NetworkNode], edges: List[NetworkEdge]) -> Dict[str, int]:
        degree = defaultdict(int)
        for edge in edges:
            degree[edge.source] += 1
            degree[edge.target] += 1
        return dict(degree)

    def _risk_map(self, nodes: List[NetworkNode], edges: List[NetworkEdge]) -> Dict[str, str]:
        risk = {}
        for node in nodes:
            if node.properties and node.properties.get("risk_level"):
                risk[node.id] = str(node.properties.get("risk_level", "Low")).capitalize()
            else:
                risk[node.id] = "Low"
        return risk

    def _find_bridge_nodes(self, nodes: List[NetworkNode], edges: List[NetworkEdge]) -> List[Dict[str, Any]]:
        """Identifies nodes that connect different communities (articulation points)."""
        if len(nodes) < 3:
            return []

        adj: Dict[str, List[str]] = defaultdict(list)
        for edge in edges:
            adj[edge.source].append(edge.target)
            adj[edge.target].append(edge.source)

        node_map = {n.id: n for n in nodes}
        bridges: List[Dict[str, Any]] = []
        seen_bridges: set = set()
        visited = set()
        disc: Dict[str, int] = {}
        low: Dict[str, int] = {}
        parent: Dict[str, str] = {}
        time = 0

        for start in nodes:
            if start.id in visited:
                continue
            root = start.id
            visited.add(root)
            disc[root] = low[root] = time
            time += 1
            parent[root] = ""
            stack = [(root, iter(adj.get(root, [])))]
            children = defaultdict(int)

            while stack:
                u, it = stack[-1]
                try:
                    v = next(it)
                    if v not in visited:
                        visited.add(v)
                        disc[v] = low[v] = time
                        time += 1
                        parent[v] = u
                        children[u] += 1
                        stack.append((v, iter(adj.get(v, []))))
                    elif v != parent.get(u):
                        low[u] = min(low[u], disc[v])
                except StopIteration:
                    stack.pop()
                    if stack:
                        p = stack[-1][0]
                        low[p] = min(low[p], low[u])
                        if parent.get(p) and low[u] >= disc[p] and p not in seen_bridges:
                            node = node_map.get(p)
                            if node:
                                seen_bridges.add(p)
                                bridges.append({
                                    "id": p,
                                    "label": node.label,
                                    "type": node.type,
                                    "connections": len(adj.get(p, [])),
                                })

            if children[root] > 1 and root not in seen_bridges:
                node = node_map.get(root)
                if node:
                    seen_bridges.add(root)
                    bridges.append({
                        "id": root,
                        "label": node.label,
                        "type": node.type,
                        "connections": len(adj.get(root, [])),
                    })

        bridges.sort(key=lambda x: x.get("connections", 0), reverse=True)
        return bridges[:20]

    def _build_timeline(self, nodes: List[NetworkNode], edges: List[NetworkEdge], crimes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        events = []
        for crime in crimes:
            ts = crime.get("CREATEDTIME", "") or crime.get("incident_date", "")
            if not ts:
                continue
            events.append({
                "date": ts[:10] if len(ts) >= 10 else ts,
                "timestamp": ts,
                "event": f"Crime recorded: {crime.get('title', crime.get('crime_type', 'Unknown'))}",
                "added_nodes": 1,
                "added_edges": 1,
                "node_id": crime.get("ROWID", ""),
                "crime_type": crime.get("crime_type", ""),
                "district_id": crime.get("district_id", ""),
            })
        events.sort(key=lambda e: e.get("date", ""))
        return events
