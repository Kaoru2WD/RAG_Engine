from pathlib import Path

from rag_engine.source_catalog import build_source_catalog


def test_build_source_catalog_adds_source_url_and_document_ref() -> None:
    catalog = build_source_catalog(Path("sample_data/documents"))

    assert catalog
    first = next(iter(catalog.values()))
    assert first.document_ref.startswith("DOC-")
    assert first.source_url.startswith("file:///")
