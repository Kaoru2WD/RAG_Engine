from rag_engine.models import ChunkRecord
from rag_engine.vector_text import build_document_embedding_text


def test_build_document_embedding_text_can_include_title_and_source() -> None:
    chunk = ChunkRecord(
        source_path="C:/docs/sample.md",
        title="sample_title",
        file_type="md",
        chunk_index=0,
        text="boot sequence checklist",
    )

    built = build_document_embedding_text(chunk, source_label="html/sample.html", mode="title_source_text")

    assert "sample_title" in built
    assert "html/sample.html" in built
    assert "boot sequence checklist" in built
