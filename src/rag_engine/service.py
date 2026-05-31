from dataclasses import asdict
from pathlib import Path

from rag_engine.answering import compose_answer
from rag_engine.config import Settings
from rag_engine.embedding_provider import build_embedding_provider
from rag_engine.hybrid_client import HybridSearchClient
from rag_engine.indexer import Indexer
from rag_engine.models import QueryResponse, RebuildResponse, SearchHitRecord
from rag_engine.retriever import Retriever
from rag_engine.source_catalog import build_source_catalog
from rag_engine.storage import IndexStore
from rag_engine.vector_indexer import VectorIndexer
from rag_engine.vector_retriever import VectorRetriever
from rag_engine.vector_storage import VectorIndexCompatibilityError, VectorIndexStore


class RagService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.store = IndexStore(settings.database_path)
        self.vector_store = VectorIndexStore(settings.vector_database_path)
        self.embedding_provider = build_embedding_provider(settings)
        self.indexer = Indexer(self.store, settings.chunk_size, settings.chunk_overlap, settings.chunk_strategy)
        self.vector_indexer = VectorIndexer(
            self.vector_store,
            self.embedding_provider,
            settings.vector_chunk_size,
            settings.vector_chunk_overlap,
            settings.vector_document_text_mode,
            settings.vector_chunk_strategy,
        )
        self.retriever = Retriever(self.store)
        self.vector_retriever = VectorRetriever(self.vector_store, self.embedding_provider)
        self.source_catalog = build_source_catalog(settings.documents_dir)

    def rebuild_index(self) -> RebuildResponse:
        documents, chunks, skipped = self.indexer.rebuild(self.settings.documents_dir)
        self.source_catalog = build_source_catalog(self.settings.documents_dir)
        return RebuildResponse(
            indexed_documents=documents,
            indexed_chunks=chunks,
            skipped_files=skipped,
        )

    def rebuild_vector_index(self) -> RebuildResponse:
        documents, chunks, skipped, provider_name, provider_detail = self.vector_indexer.rebuild(self.settings.documents_dir)
        self.source_catalog = build_source_catalog(self.settings.documents_dir)
        return RebuildResponse(
            indexed_documents=documents,
            indexed_chunks=chunks,
            skipped_files=skipped,
            provider_name=provider_name,
            provider_detail=provider_detail,
        )

    def query(self, question: str, top_k: int) -> QueryResponse:
        raw_hits = self.retriever.retrieve(question, top_k)
        hits = [self._enrich_local_hit(hit) for hit in raw_hits]
        answer = compose_answer(question, raw_hits)
        return QueryResponse(
            question=question,
            engine="bm25_server",
            answer=answer,
            hits=[asdict(hit) for hit in hits],
            backend_status="local",
        )

    def query_vector(self, question: str, top_k: int) -> QueryResponse:
        try:
            raw_hits = self.vector_retriever.retrieve(question, top_k)
        except VectorIndexCompatibilityError as exc:
            raise ValueError(str(exc)) from exc
        hits = [self._enrich_local_hit(hit) for hit in raw_hits]
        answer = compose_answer(question, raw_hits)
        provider_meta = self.vector_store.metadata()
        return QueryResponse(
            question=question,
            engine="vector_server",
            answer=answer,
            hits=[asdict(hit) for hit in hits],
            backend_status=provider_meta.get("provider_name", "local"),
        )

    def query_hybrid(self, question: str, top_k: int) -> QueryResponse:
        if not self.settings.hybrid_backend_url:
            raise ValueError("Hybrid backend URL is not configured.")
        client = HybridSearchClient(
            backend_url=self.settings.hybrid_backend_url,
            timeout_seconds=self.settings.hybrid_backend_timeout_seconds,
        )
        return client.search(question=question, top_k=top_k, source_catalog=self.source_catalog)

    def hybrid_backend_query(self, question: str, top_k: int) -> dict:
        try:
            raw_hits = self.vector_retriever.retrieve(question, top_k)
        except VectorIndexCompatibilityError as exc:
            raise ValueError(str(exc)) from exc
        hits = [self._enrich_local_hit(hit) for hit in raw_hits]
        return {
            "answer": "",
            "backend_status": "connected",
            "hits": [
                {
                    "source_path": hit.source_path,
                    "source_url": hit.source_url,
                    "source_label": hit.source_label,
                    "title": hit.title,
                    "file_type": hit.file_type,
                    "chunk_index": hit.chunk_index,
                    "score": hit.score,
                    "text": hit.text,
                    "document_ref": hit.document_ref,
                    "placeholder_keys": hit.placeholder_keys,
                }
                for hit in hits
            ],
        }

    def _enrich_local_hit(self, hit) -> SearchHitRecord:
        entry = self.source_catalog.get(str(Path(hit.source_path).resolve()))
        if entry is None:
            source_path = str(Path(hit.source_path).resolve())
            return SearchHitRecord(
                chunk_id=hit.chunk_id,
                document_ref="DOC-UNK",
                source_path=source_path,
                source_label=Path(source_path).name,
                source_url=Path(source_path).resolve().as_uri(),
                title=hit.title,
                file_type=hit.file_type,
                chunk_index=hit.chunk_index,
                score=hit.score,
                text=hit.text,
                placeholder_keys=[],
            )

        return SearchHitRecord(
            chunk_id=hit.chunk_id,
            document_ref=entry.document_ref,
            source_path=entry.source_path,
            source_label=entry.source_label,
            source_url=entry.source_url,
            title=hit.title,
            file_type=hit.file_type,
            chunk_index=hit.chunk_index,
            score=hit.score,
            text=hit.text,
            placeholder_keys=[],
        )
