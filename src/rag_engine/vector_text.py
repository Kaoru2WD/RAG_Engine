from rag_engine.models import ChunkRecord


def build_document_embedding_text(chunk: ChunkRecord, source_label: str, mode: str) -> str:
    normalized_mode = normalize_document_text_mode(mode)
    if normalized_mode == "text":
        return chunk.text
    if normalized_mode == "title_source_text":
        return "\n".join(
            [
                f"title: {chunk.title}",
                f"source: {source_label}",
                chunk.text,
            ]
        )
    raise ValueError(f"Unsupported vector document text mode: {mode}")


def normalize_document_text_mode(mode: str) -> str:
    lowered = mode.strip().lower()
    aliases = {
        "text": "text",
        "body": "text",
        "body_only": "text",
        "title_source_text": "title_source_text",
        "title+source+text": "title_source_text",
        "title_source_label_text": "title_source_text",
    }
    if lowered not in aliases:
        raise ValueError(f"Unsupported vector document text mode: {mode}")
    return aliases[lowered]
