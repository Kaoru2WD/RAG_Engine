from rag_engine.models import ChunkRecord, DocumentRecord


def chunk_document(document: DocumentRecord, chunk_size: int, overlap: int) -> list[ChunkRecord]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        raise ValueError("overlap must be non-negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    text = normalize_text(document.content)
    if not text:
        return []

    chunks: list[ChunkRecord] = []
    start = 0
    step = chunk_size - overlap
    chunk_index = 0

    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(
                ChunkRecord(
                    source_path=str(document.source_path),
                    title=document.title,
                    file_type=document.file_type,
                    chunk_index=chunk_index,
                    text=chunk_text,
                )
            )
            chunk_index += 1
        if end >= len(text):
            break
        start += step

    return chunks


def normalize_text(text: str) -> str:
    collapsed_lines = (line.strip() for line in text.replace("\r\n", "\n").split("\n"))
    return "\n".join(line for line in collapsed_lines if line)
