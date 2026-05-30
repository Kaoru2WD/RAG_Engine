from fastapi import FastAPI

from rag_engine.config import settings
from rag_engine.service import RagService

app = FastAPI(title="RAG Engine Dev Hybrid Stub")
service = RagService(settings)


@app.post("/query")
def query(payload: dict) -> dict:
    question = str(payload.get("question", ""))
    top_k = int(payload.get("top_k", settings.default_top_k))
    response = service.query_vector(question, top_k)
    return {
        "answer": response.answer,
        "backend_status": "dev_hybrid_stub",
        "hits": response.hits,
    }
