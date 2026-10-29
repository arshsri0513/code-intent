from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., description="Developer natural language query explaining why code is written this way")
    repo_id: Optional[str] = Field("sample-gateway", description="Repository identifier to query")

class EvidenceItem(BaseModel):
    source_type: str = Field(..., description="PR, Commit, Issue, or Incident")
    identifier: str = Field(..., description="e.g. PR #114 or Commit e89f2a1")
    title: str
    author: str
    timestamp: str
    url: Optional[str] = None
    snippet: Optional[str] = None

class SupersessionInfo(BaseModel):
    is_superseded: bool
    status: str = Field("ACTIVE", description="ACTIVE, SUPERSEDED, or DEPRECATED")
    superseded_by: Optional[str] = None
    superseded_at: Optional[str] = None
    reason: Optional[str] = None

class QueryResponse(BaseModel):
    success: bool
    query: str
    target_entity: Optional[str] = None
    governing_decision: str
    evidence_chain: List[EvidenceItem]
    supersession: SupersessionInfo
    who_to_ask: Optional[str] = None
    confidence_score: float = Field(..., description="Confidence score between 0.0 and 1.0")
    confidence_rationale: str
    graph_subgraph: Optional[Dict[str, Any]] = None

class IngestRequest(BaseModel):
    repo_url: str
    branch: Optional[str] = "main"

class GraphNode(BaseModel):
    id: str
    label: str
    type: str # CodeEntity, Decision, PR, Commit, Incident, Contributor
    properties: Dict[str, Any] = {}

class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str # MODIFIES, INTRODUCES, RESOLVES, SUPERSEDES, AUTHORED_BY

class GraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
