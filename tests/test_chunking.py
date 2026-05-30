from pathlib import Path

from rag_engine.chunking import chunk_document
from rag_engine.models import DocumentRecord


def test_chunk_document_creates_overlapping_chunks() -> None:
    document = DocumentRecord(
        source_path=Path("sample.md"),
        title="sample",
        file_type="md",
        content="A" * 1500,
    )

    chunks = chunk_document(document, chunk_size=800, overlap=100)

    assert len(chunks) == 2
    assert len(chunks[0].text) == 800
    assert len(chunks[1].text) == 800
    assert chunks[0].text[-100:] == chunks[1].text[:100]
