import os
import json
import logging
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger("graph_engine")

class GraphEngine:
    def __init__(self, sample_path: Optional[str] = None):
        self.neo4j_uri = os.getenv("NEO4J_URI")
        self.neo4j_user = os.getenv("NEO4J_USERNAME", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD")
        self.use_neo4j = False
        self.driver = None

        # Pure Python high-performance graph engine (adjacency map)
        self.nodes_data: Dict[str, Dict[str, Any]] = {}
        self.edges_data: List[Dict[str, Any]] = []
        self.adj_out: Dict[str, Set[str]] = {}
        self.adj_in: Dict[str, Set[str]] = {}

        if sample_path and os.path.exists(sample_path):
            self.load_from_json(sample_path)

        if self.neo4j_uri and self.neo4j_password:
            try:
                from neo4j import GraphDatabase
                self.driver = GraphDatabase.driver(
                    self.neo4j_uri,
                    auth=(self.neo4j_user, self.neo4j_password)
                )
                self.driver.verify_connectivity()
                self.use_neo4j = True
                logger.info("Connected to remote Neo4j AuraDB instance.")
            except Exception as e:
                logger.warning(f"Neo4j connection failed ({e}). Falling back to built-in pure-Python graph engine.")

    def load_from_json(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for n in data.get("nodes", []):
            nid = n["id"]
            self.nodes_data[nid] = n
            self.adj_out[nid] = set()
            self.adj_in[nid] = set()

        for e in data.get("edges", []):
            self.edges_data.append(e)
            src, tgt = e["source"], e["target"]
            if src not in self.adj_out:
                self.adj_out[src] = set()
            if tgt not in self.adj_in:
                self.adj_in[tgt] = set()
            self.adj_out[src].add(tgt)
            self.adj_in[tgt].add(src)

        logger.info(f"Loaded {len(self.nodes_data)} nodes and {len(self.edges_data)} edges into GraphEngine.")

    def get_all_graph(self) -> Dict[str, Any]:
        return {
            "nodes": list(self.nodes_data.values()),
            "edges": self.edges_data
        }

    def find_node_by_keyword(self, keywords: List[str]) -> Optional[Dict[str, Any]]:
        for kw in keywords:
            kw_lower = kw.lower()
            for nid, node in self.nodes_data.items():
                label = node.get("label", "").lower()
                props = str(node.get("properties", {})).lower()
                if kw_lower in label or kw_lower in props:
                    return node
        return None

    def get_connected_subgraph(self, start_node_id: str) -> Dict[str, Any]:
        """Traverse incoming and outgoing edges to find the causal cluster."""
        visited_nodes: Set[str] = {start_node_id}
        frontier = [start_node_id]

        # 2-hop radius traversal
        for _ in range(2):
            next_frontier = []
            for curr in frontier:
                neighbors = list(self.adj_in.get(curr, set())) + list(self.adj_out.get(curr, set()))
                for n in neighbors:
                    if n not in visited_nodes:
                        visited_nodes.add(n)
                        next_frontier.append(n)
            frontier = next_frontier

        subgraph_nodes = [self.nodes_data[nid] for nid in visited_nodes if nid in self.nodes_data]
        subgraph_edges = [
            e for e in self.edges_data
            if e["source"] in visited_nodes and e["target"] in visited_nodes
        ]
        return {"nodes": subgraph_nodes, "edges": subgraph_edges}

    def close(self):
        if self.driver:
            self.driver.close()
