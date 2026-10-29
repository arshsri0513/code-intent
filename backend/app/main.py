import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Ensure app package is importable
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.models.schemas import QueryRequest, QueryResponse, IngestRequest
from app.graph.neo4j_client import GraphEngine
from app.rag.graph_rag import GraphRAGEngine

app = FastAPI(
    title="Why The Code Is Like This - Evidence GraphRAG API",
    description="Applied AI Platform for Codebase Archaeology & Intent Retrieval (hackFront India 2026)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Graph Engine with sample data
sample_data_path = os.path.join(current_dir, "data", "sample_graph.json")
graph_engine = GraphEngine(sample_path=sample_data_path)
rag_engine = GraphRAGEngine(graph_engine=graph_engine)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "why-the-code-is-like-this",
        "team": "HACK1MAW",
        "author": "Ansh Srivastava (arshsri0513)",
        "track": "AI and Developer Tools",
        "engine": "Neo4j / GraphRAG"
    }

@app.get("/api/repositories")
def get_repositories():
    return [
        {
            "id": "sample-gateway",
            "name": "enterprise-auth-gateway",
            "url": "https://github.com/arshsri0513/why-the-code-is-like-this",
            "status": "INDEXED",
            "entities_indexed": 16,
            "decisions_tracked": 5
        }
    ]

@app.get("/api/graph")
def get_full_graph():
    return graph_engine.get_all_graph()

@app.post("/api/query", response_model=QueryResponse)
def query_code_intent(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    return rag_engine.answer_query(req.query)

@app.post("/api/ingest")
def trigger_ingest(req: IngestRequest):
    return {
        "status": "success",
        "message": f"Successfully queued ingestion for {req.repo_url} on branch {req.branch}.",
        "task_id": "ingest_task_001"
    }

# Serve frontend static assets if available
frontend_path = os.path.join(parent_dir, "..", "frontend")
if os.path.exists(frontend_path):
    @app.get("/")
    def serve_index():
        index_file = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "CodeIntent API running. Frontend index.html not found."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
