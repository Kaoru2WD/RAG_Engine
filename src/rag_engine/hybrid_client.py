from pathlib import Path
from dataclasses import asdict

import httpx

from rag_engine.models import QueryResponse, SearchHitRecord
from rag_engine.source_catalog import DocumentCatalogEntry


class HybridSearchClient:
    def __init__(self, backend_url: str, timeout_seconds: float) -> None:
        self.backend_url = backend_url
        self.timeout_seconds = timeout_seconds

    def search(
        self,
        question: str,
        top_k: int,
        source_catalog: dict[str, DocumentCatalogEntry],
    ) -> QueryResponse:
        response = httpx.post(
            self.backend_url,
            json={"question": question, "top_k": top_k},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()

        hits = [
            _normalize_hit(index, raw_hit, source_catalog)
            for index, raw_hit in enumerate(payload.get("hits", []))
        ]

        return QueryResponse(
            question=question,
            engine="hybrid_server",
            answer=payload.get("answer", ""),
            hits=[asdict(hit) for hit in hits],
            backend_status=payload.get("backend_status", "connected"),
        )


def _normalize_hit(
    index: int,
    raw_hit: dict,
    source_catalog: dict[str, DocumentCatalogEntry],
) -> SearchHitRecord:
    source_path = raw_hit.get("source_path")
    resolved_source_path = str(Path(source_path).resolve()) if source_path else None
    catalog_entry = source_catalog.get(resolved_source_path) if resolved_source_path else None

    document_ref = raw_hit.get("document_ref") or (catalog_entry.document_ref if catalog_entry else f"EXT-{index + 1:03d}")
    source_label = raw_hit.get("source_label") or (catalog_entry.source_label if catalog_entry else source_path or "(external)")
    source_url = raw_hit.get("source_url") or (catalog_entry.source_url if catalog_entry else "")
    title = raw_hit.get("title") or (catalog_entry.title if catalog_entry else source_label)
    file_type = raw_hit.get("file_type") or (catalog_entry.file_type if catalog_entry else "")

    return SearchHitRecord(
        chunk_id=raw_hit.get("chunk_id"),
        document_ref=document_ref,
        source_path=resolved_source_path,
        source_label=source_label,
        source_url=source_url,
        title=title,
        file_type=file_type,
        chunk_index=int(raw_hit.get("chunk_index", 0)),
        score=float(raw_hit.get("score", 0.0)),
        text=raw_hit.get("text", ""),
        placeholder_keys=list(raw_hit.get("placeholder_keys", [])),
    )
