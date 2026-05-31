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


def test_chunk_document_heading_strategy_preserves_sections() -> None:
    document = DocumentRecord(
        source_path=Path("sample.md"),
        title="sample",
        file_type="md",
        content=(
            "# Root\n"
            "intro line\n"
            "## Preconditions\n"
            "12V ready\n"
            "HV standby\n"
            "## Boot Steps\n"
            "step 1\n"
            "step 2\n"
            "## Verification\n"
            "ready state"
        ),
    )

    chunks = chunk_document(document, chunk_size=40, overlap=10, strategy="heading")

    assert len(chunks) >= 3
    assert "## Preconditions" in "".join(chunk.text for chunk in chunks)
    assert "## Boot Steps" in "".join(chunk.text for chunk in chunks)
