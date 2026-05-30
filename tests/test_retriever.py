from pathlib import Path

from rag_engine.chunking import chunk_document
from rag_engine.models import DocumentRecord
from rag_engine.retriever import Retriever
from rag_engine.storage import IndexStore


def test_retriever_returns_matching_chunk(tmp_path: Path) -> None:
    store = IndexStore(tmp_path / "index.sqlite3")
    document = DocumentRecord(
        source_path=Path("can_troubleshooting.md"),
        title="can_troubleshooting",
        file_type="md",
        content="CAN通信異常時は終端抵抗とボーレートを確認する。",
    )
    chunks = chunk_document(document, chunk_size=100, overlap=10)
    store.add_chunks(chunks)

    retriever = Retriever(store)
    hits = retriever.retrieve("終端抵抗", top_k=3)

    assert hits
    assert hits[0].title == "can_troubleshooting"
