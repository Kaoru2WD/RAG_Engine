from dataclasses import dataclass
from pathlib import Path

from rag_engine.extractors import discover_documents


@dataclass(slots=True)
class DocumentCatalogEntry:
    document_ref: str
    source_path: str
    source_label: str
    source_url: str
    title: str
    file_type: str


def build_source_catalog(documents_dir: Path) -> dict[str, DocumentCatalogEntry]:
    catalog: dict[str, DocumentCatalogEntry] = {}
    for index, path in enumerate(discover_documents(documents_dir), start=1):
        catalog[str(path.resolve())] = DocumentCatalogEntry(
            document_ref=f"DOC-{index:03d}",
            source_path=str(path.resolve()),
            source_label=str(path.relative_to(documents_dir)),
            source_url=path.resolve().as_uri(),
            title=path.stem,
            file_type=path.suffix.lstrip("."),
        )
    return catalog
