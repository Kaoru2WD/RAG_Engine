from pathlib import Path

from rag_engine.chunking import chunk_document
from rag_engine.embedding_provider import LocalHashEmbeddingProvider
from rag_engine.models import DocumentRecord
from rag_engine.service import RagService
from rag_engine.vector_storage import VectorIndexStore


def test_hybrid_backend_query_returns_expected_contract(tmp_path: Path) -> None:
    service = RagService.__new__(RagService)
    service.source_catalog = {}
    service.vector_store = VectorIndexStore(tmp_path / "vector.sqlite3")
    service.embedding_provider = LocalHashEmbeddingProvider(dimensions=256)
    from rag_engine.vector_retriever import VectorRetriever

    service.vector_retriever = VectorRetriever(service.vector_store, service.embedding_provider)

    document = DocumentRecord(
        source_path=Path("inverter_boot_sequence_checklist.html"),
        title="inverter_boot_sequence_checklist",
        file_type="html",
        content="inverter boot sequence checklist startup bringup",
    )
    chunks = chunk_document(document, chunk_size=120, overlap=20)
    batch = service.embedding_provider.embed_texts([chunk.text for chunk in chunks])
    service.vector_store.add_chunks(
        chunks,
        batch.vectors,
        batch.provider_name,
        batch.detail,
        document_text_mode="text",
        chunk_size=120,
        chunk_overlap=20,
    )

    from rag_engine.service import RagService as RagServiceClass

    payload = RagServiceClass.hybrid_backend_query(service, "boot sequence", 1)

    assert payload["backend_status"] == "connected"
    assert payload["answer"] == ""
    assert payload["hits"]
    assert "source_path" in payload["hits"][0]
    assert "source_url" in payload["hits"][0]
