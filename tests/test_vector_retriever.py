from pathlib import Path

from rag_engine.chunking import chunk_document
from rag_engine.embedding_provider import LocalHashEmbeddingProvider
from rag_engine.models import DocumentRecord
from rag_engine.vector_retriever import VectorRetriever
from rag_engine.vector_storage import VectorIndexStore


def test_vector_retriever_returns_semantically_close_chunk(tmp_path: Path) -> None:
    store = VectorIndexStore(tmp_path / "vector.sqlite3")
    provider = LocalHashEmbeddingProvider(dimensions=256)
    document = DocumentRecord(
        source_path=Path("power_mode.md"),
        title="power_mode",
        file_type="md",
        content=(
            "HILSのPRECHARGE滞留時はPSU current limitとHV bus voltageを確認する。\n"
            "READY遷移後のTorqueEnableReqも見る。"
        ),
    )
    chunks = chunk_document(document, chunk_size=120, overlap=20)
    batch = provider.embed_texts([chunk.text for chunk in chunks])
    store.add_chunks(
        chunks,
        batch.vectors,
        batch.provider_name,
        batch.detail,
        document_text_mode="text",
        chunk_size=120,
        chunk_overlap=20,
    )

    retriever = VectorRetriever(store, provider)
    hits = retriever.retrieve("precharge stall の確認項目", top_k=3)

    assert hits
    assert hits[0].title == "power_mode"
    assert hits[0].score > 0
