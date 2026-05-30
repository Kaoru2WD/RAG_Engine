import argparse
import json
from pathlib import Path

from rag_engine.config import settings
from rag_engine.embedding_provider import build_embedding_provider
from rag_engine.vector_indexer import VectorIndexer
from rag_engine.vector_storage import VectorIndexStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a vector-style chunk database for the local HILS samples.")
    parser.add_argument("--documents-dir", default=str(settings.documents_dir))
    parser.add_argument("--database-path", default=str(settings.vector_database_path))
    parser.add_argument("--chunk-size", type=int, default=settings.vector_chunk_size)
    parser.add_argument("--chunk-overlap", type=int, default=settings.vector_chunk_overlap)
    parser.add_argument("--document-text-mode", default=settings.vector_document_text_mode)
    args = parser.parse_args()

    vector_settings = settings.model_copy(
        update={
            "documents_dir": Path(args.documents_dir),
            "vector_database_path": Path(args.database_path),
            "vector_chunk_size": args.chunk_size,
            "vector_chunk_overlap": args.chunk_overlap,
            "vector_document_text_mode": args.document_text_mode,
        }
    )
    store = VectorIndexStore(vector_settings.vector_database_path)
    provider = build_embedding_provider(vector_settings)
    indexer = VectorIndexer(
        store,
        provider,
        vector_settings.vector_chunk_size,
        vector_settings.vector_chunk_overlap,
        vector_settings.vector_document_text_mode,
    )
    indexed_documents, indexed_chunks, skipped_files, provider_name, provider_detail = indexer.rebuild(
        vector_settings.documents_dir
    )
    payload = {
        "indexed_documents": indexed_documents,
        "indexed_chunks": indexed_chunks,
        "skipped_files": skipped_files,
        "database_path": str(vector_settings.vector_database_path),
        "provider_name": provider_name,
        "provider_detail": provider_detail,
        "document_text_mode": vector_settings.vector_document_text_mode,
        "chunk_size": vector_settings.vector_chunk_size,
        "chunk_overlap": vector_settings.vector_chunk_overlap,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
