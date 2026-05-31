from pathlib import Path

from rag_engine.chunking import chunk_document
from rag_engine.embedding_provider import BaseEmbeddingProvider
from rag_engine.extractors import discover_documents, extract_document
from rag_engine.vector_storage import VectorIndexStore
from rag_engine.vector_text import build_document_embedding_text


class VectorIndexer:
    def __init__(
        self,
        store: VectorIndexStore,
        embedding_provider: BaseEmbeddingProvider,
        chunk_size: int,
        chunk_overlap: int,
        document_text_mode: str,
        chunk_strategy: str = "fixed",
    ) -> None:
        self.store = store
        self.embedding_provider = embedding_provider
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.document_text_mode = document_text_mode
        self.chunk_strategy = chunk_strategy

    def rebuild(self, documents_dir: Path) -> tuple[int, int, list[str], str, str]:
        self.store.reset()
        indexed_documents = 0
        indexed_chunks = 0
        skipped_files: list[str] = []
        provider_name = "unknown"
        provider_detail = "not_used"

        for path in discover_documents(documents_dir):
            try:
                document = extract_document(path)
                chunks = chunk_document(document, self.chunk_size, self.chunk_overlap, strategy=self.chunk_strategy)
                source_label = str(path.relative_to(documents_dir))
                embedding_inputs = [
                    build_document_embedding_text(chunk, source_label=source_label, mode=self.document_text_mode)
                    for chunk in chunks
                ]
                batch = self.embedding_provider.embed_texts(embedding_inputs)
                provider_name = batch.provider_name
                provider_detail = batch.detail
                indexed_chunks += self.store.add_chunks(
                    chunks,
                    batch.vectors,
                    provider_name,
                    provider_detail,
                    document_text_mode=self.document_text_mode,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                    chunk_strategy=self.chunk_strategy,
                )
                indexed_documents += 1
            except Exception as exc:  # noqa: BLE001
                skipped_files.append(f"{path}: {exc}")

        return indexed_documents, indexed_chunks, skipped_files, provider_name, provider_detail
