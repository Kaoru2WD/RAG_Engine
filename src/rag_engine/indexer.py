from pathlib import Path

from rag_engine.chunking import chunk_document
from rag_engine.extractors import discover_documents, extract_document
from rag_engine.storage import IndexStore


class Indexer:
    def __init__(self, store: IndexStore, chunk_size: int, chunk_overlap: int, chunk_strategy: str = "fixed") -> None:
        self.store = store
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunk_strategy = chunk_strategy

    def rebuild(self, documents_dir: Path) -> tuple[int, int, list[str]]:
        self.store.reset()
        indexed_documents = 0
        indexed_chunks = 0
        skipped_files: list[str] = []

        for path in discover_documents(documents_dir):
            try:
                document = extract_document(path)
                chunks = chunk_document(document, self.chunk_size, self.chunk_overlap, strategy=self.chunk_strategy)
                indexed_chunks += self.store.add_chunks(chunks)
                indexed_documents += 1
            except Exception as exc:  # noqa: BLE001
                skipped_files.append(f"{path}: {exc}")

        return indexed_documents, indexed_chunks, skipped_files
