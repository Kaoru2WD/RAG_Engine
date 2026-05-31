from pathlib import Path

from fastapi.testclient import TestClient

from rag_engine.chunking import chunk_document
from rag_engine.config import Settings
from rag_engine.embedding_provider import LocalHashEmbeddingProvider
import rag_engine.main as main_module
from rag_engine.main import create_app
from rag_engine.models import DocumentRecord
from rag_engine.vector_storage import VectorIndexStore


def test_query_vector_returns_503_on_dimension_mismatch(tmp_path: Path, monkeypatch) -> None:
    vector_database_path = tmp_path / "vector.sqlite3"
    store = VectorIndexStore(vector_database_path)
    index_provider = LocalHashEmbeddingProvider(dimensions=256)
    document = DocumentRecord(
        source_path=Path("power_mode.md"),
        title="power_mode",
        file_type="md",
        content="PRECHARGE stall の確認項目と HV bus voltage を確認する。",
    )
    chunks = chunk_document(document, chunk_size=120, overlap=20)
    batch = index_provider.embed_texts([chunk.text for chunk in chunks])
    store.add_chunks(
        chunks,
        batch.vectors,
        batch.provider_name,
        batch.detail,
        document_text_mode="text",
        chunk_size=120,
        chunk_overlap=20,
    )

    patched_settings = Settings(
        vector_database_path=vector_database_path,
        vector_embedding_provider="local-hash",
        local_vector_dimensions=512,
    )
    monkeypatch.setattr("rag_engine.config.settings", patched_settings)
    monkeypatch.setattr(main_module, "settings", patched_settings)

    app = create_app()
    client = TestClient(app)
    response = client.post("/query", json={"question": "precharge stall", "top_k": 3, "engine": "vector"})

    assert response.status_code == 503
    assert "Vector index embedding dimensions do not match" in response.json()["detail"]
