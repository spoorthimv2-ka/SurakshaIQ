from typing import List, Optional, Any
from neo4j import AsyncSession
from app.schemas.offender import OffenderSummary

class OffenderGraphRepository:
    def __init__(self, session: Optional[AsyncSession]):
        self.session = session

    def _classify_risk(self, count: int) -> str:
        """
        Calculates a placeholder risk score based on the number of offenses.
        TODO: Align this logic with explicit PRD/TRD thresholds once available.
        """
        if count >= 3:
            return "HIGH"
        elif count == 2:
            return "MEDIUM"
        else:
            return "LOW"

    async def get_repeat_offenders(self, skip: int = 0, limit: int = 20) -> tuple[List[OffenderSummary], int]:
        """
        Fetches repeat offenders from Neo4j.
        Returns a tuple of (list of offenders, total_count).
        """
        if not self.session:
            return [], 0

        # Query to fetch offenders linked to multiple crimes
        # We assume a schema like (o:Offender)-[:COMMITTED]->(c:Crime)
        query = """
        MATCH (o:Offender)-[:COMMITTED]->(c:Crime)
        WITH o, count(c) AS offense_count, collect(c.id) AS case_ids
        WHERE offense_count > 1
        RETURN o.id AS id, o.name AS name, offense_count, case_ids, o.last_location AS location
        ORDER BY offense_count DESC
        SKIP $skip LIMIT $limit
        """
        
        count_query = """
        MATCH (o:Offender)-[:COMMITTED]->(c:Crime)
        WITH o, count(c) AS offense_count
        WHERE offense_count > 1
        RETURN count(o) AS total
        """

        try:
            # Execute Count
            count_result = await self.session.run(count_query)
            count_record = await count_result.single()
            total_count = count_record["total"] if count_record else 0
            
            # Execute Fetch
            result = await self.session.run(query, skip=skip, limit=limit)
            records = await result.data()

            offenders = []
            for rec in records:
                offense_count = rec["offense_count"]
                offenders.append(
                    OffenderSummary(
                        offender_id=str(rec["id"]),
                        name=rec["name"],
                        risk_classification=self._classify_risk(offense_count),
                        offense_count=offense_count,
                        associated_case_ids=[str(cid) for cid in rec["case_ids"]],
                        last_known_location=rec.get("location")
                    )
                )

            return offenders, total_count
        except Exception as e:
            # If the database is completely empty or schema doesn't exist, it might error.
            print(f"Error querying Neo4j for offenders: {e}")
            return [], 0

    async def get_offender_by_id(self, offender_id: str) -> Optional[OffenderSummary]:
        if not self.session:
            return None

        query = """
        MATCH (o:Offender {id: $offender_id})-[:COMMITTED]->(c:Crime)
        WITH o, count(c) AS offense_count, collect(c.id) AS case_ids
        RETURN o.id AS id, o.name AS name, offense_count, case_ids, o.last_location AS location
        """
        
        try:
            result = await self.session.run(query, offender_id=offender_id)
            rec = await result.single()
            if not rec:
                return None
                
            offense_count = rec["offense_count"]
            return OffenderSummary(
                offender_id=str(rec["id"]),
                name=rec["name"],
                risk_classification=self._classify_risk(offense_count),
                offense_count=offense_count,
                associated_case_ids=[str(cid) for cid in rec["case_ids"]],
                last_known_location=rec.get("location")
            )
        except Exception as e:
            print(f"Error querying Neo4j for offender by id: {e}")
            return None

    async def get_offender_network(self, offender_id: str) -> dict:
        """
        Retrieves the 1-hop and 2-hop network around an offender.
        Returns a dict suitable for D3 node/link visualization.
        """
        if not self.session:
            return {"nodes": [], "links": []}

        # Find the focal offender, their crimes, and co-offenders
        query = """
        MATCH (o1:Offender {id: $offender_id})-[:COMMITTED]->(c:Crime)
        OPTIONAL MATCH (c)<-[:COMMITTED]-(o2:Offender)
        WHERE o1 <> o2
        RETURN o1, c, o2
        """

        try:
            result = await self.session.run(query, offender_id=offender_id)
            records = await result.data()
            
            nodes_dict = {}
            links_list = []
            
            def add_node(n_id, label, n_type, props):
                if n_id not in nodes_dict:
                    nodes_dict[n_id] = {"id": str(n_id), "label": label, "type": n_type, "properties": props}

            for rec in records:
                o1 = rec.get("o1")
                if o1:
                    add_node(o1.get("id"), o1.get("name", "Unknown"), "Offender", dict(o1.items()))
                
                c = rec.get("c")
                if c:
                    add_node(c.get("id"), c.get("title", f"Crime {c.get('id')}"), "Crime", dict(c.items()))
                    # Add link from o1 to c
                    links_list.append({"source": str(o1.get("id")), "target": str(c.get("id")), "type": "COMMITTED", "properties": {}})
                
                o2 = rec.get("o2")
                if o2 and c:
                    add_node(o2.get("id"), o2.get("name", "Unknown"), "Offender", dict(o2.items()))
                    # Add link from o2 to c
                    links_list.append({"source": str(o2.get("id")), "target": str(c.get("id")), "type": "COMMITTED", "properties": {}})

            # Deduplicate links
            unique_links = []
            seen = set()
            for lnk in links_list:
                sig = (lnk["source"], lnk["target"], lnk["type"])
                if sig not in seen:
                    seen.add(sig)
                    unique_links.append(lnk)

            return {
                "nodes": list(nodes_dict.values()),
                "links": unique_links
            }
        except Exception as e:
            print(f"Error retrieving offender network: {e}")
            return {"nodes": [], "links": []}
