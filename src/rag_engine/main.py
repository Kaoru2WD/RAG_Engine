from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from rag_engine.config import settings
from rag_engine.models import QueryRequest, QueryResponse, RebuildResponse
from rag_engine.runtime_paths import resolve_web_dir
from rag_engine.service import RagService

def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    service = RagService(settings)
    web_dir = resolve_web_dir()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/ui-assets", StaticFiles(directory=web_dir), name="ui-assets")

    @app.get("/")
    def root() -> RedirectResponse:
        return RedirectResponse(url="/ui")

    @app.get("/ui")
    def ui() -> FileResponse:
        return FileResponse(web_dir / "index.html")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/index/rebuild", response_model=RebuildResponse)
    def rebuild_index() -> RebuildResponse:
        return service.rebuild_index()

    @app.post("/index/rebuild-vector", response_model=RebuildResponse)
    def rebuild_vector_index() -> RebuildResponse:
        return service.rebuild_vector_index()

    @app.post("/query", response_model=QueryResponse)
    def query_documents(request: QueryRequest) -> QueryResponse:
        if request.engine == "vector":
            return service.query_vector(request.question, request.top_k)
        return service.query(request.question, request.top_k)

    @app.post("/query/hybrid", response_model=QueryResponse)
    def query_hybrid_documents(request: QueryRequest) -> QueryResponse:
        try:
            return service.query_hybrid(request.question, request.top_k)
        except ValueError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.post("/backend/query")
    def backend_query(request: QueryRequest) -> dict:
        return service.hybrid_backend_query(request.question, request.top_k)

    return app


app = create_app()
