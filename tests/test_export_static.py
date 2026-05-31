import json
from pathlib import Path

from rag_engine.export_static import build_static_index, write_static_index


def test_build_static_index_contains_redacted_chunks() -> None:
    payload, dry_run = build_static_index(
        Path("sample_data/documents"),
        placeholder_path=Path("placeholder_rules.example.json"),
        forms_request_url="https://example.com/forms/request",
    )

    assert payload["meta"]["document_count"] == 3
    assert payload["chunks"]
    assert "source_path" not in payload["chunks"][0]
    assert payload["chunks"][0]["source_url"].startswith("file:///")
    assert payload["documents"][0]["chunk_count"] >= 1
    assert payload["documents"][0]["categories"]["content_kind"]
    assert payload["meta"]["forms_request_url"] == "https://example.com/forms/request"
    assert dry_run["chunks"][0]["raw_sha256"]


def test_write_static_index_creates_assignable_js(tmp_path: Path) -> None:
    output_path = write_static_index(
        tmp_path / "search-data.js",
        Path("sample_data/documents"),
        placeholder_path=Path("placeholder_rules.example.json"),
    )

    content = output_path.read_text(encoding="utf-8")
    assert content.startswith("window.SEARCH_DATA = ")
    payload = json.loads(content.removeprefix("window.SEARCH_DATA = ").removesuffix(";\n"))
    assert "placeholder_catalog" in payload["meta"]
