from rag_engine.models import ChunkRecord, DocumentRecord


def chunk_document(document: DocumentRecord, chunk_size: int, overlap: int, strategy: str = "fixed") -> list[ChunkRecord]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        raise ValueError("overlap must be non-negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    text = normalize_text(document.content)
    if not text:
        return []

    normalized_strategy = normalize_chunk_strategy(strategy)
    if normalized_strategy == "heading":
        return _chunk_document_by_heading(document, text, chunk_size, overlap)
    return _chunk_document_fixed(document, text, chunk_size, overlap)


def normalize_chunk_strategy(strategy: str) -> str:
    lowered = strategy.strip().lower()
    aliases = {
        "fixed": "fixed",
        "fixed_length": "fixed",
        "sliding": "fixed",
        "heading": "heading",
        "headings": "heading",
        "heading_based": "heading",
        "section": "heading",
        "sections": "heading",
    }
    if lowered not in aliases:
        raise ValueError(f"Unsupported chunk strategy: {strategy}")
    return aliases[lowered]


def _chunk_document_fixed(document: DocumentRecord, text: str, chunk_size: int, overlap: int) -> list[ChunkRecord]:
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


def _chunk_document_by_heading(document: DocumentRecord, text: str, chunk_size: int, overlap: int) -> list[ChunkRecord]:
    sections = _split_into_sections(text)
    if not sections:
        return _chunk_document_fixed(document, text, chunk_size, overlap)

    combined_sections: list[str] = []
    buffer = ""
    soft_limit = max(int(chunk_size * 1.25), chunk_size + overlap)
    for section in sections:
        candidate = section if not buffer else f"{buffer}\n\n{section}"
        if buffer and len(candidate) > soft_limit:
            combined_sections.append(buffer)
            buffer = section
        else:
            buffer = candidate
    if buffer:
        combined_sections.append(buffer)

    chunks: list[ChunkRecord] = []
    chunk_index = 0
    for section in combined_sections:
        if len(section) <= chunk_size:
            chunks.append(
                ChunkRecord(
                    source_path=str(document.source_path),
                    title=document.title,
                    file_type=document.file_type,
                    chunk_index=chunk_index,
                    text=section,
                )
            )
            chunk_index += 1
            continue

        section_document = DocumentRecord(
            source_path=document.source_path,
            content=section,
            title=document.title,
            file_type=document.file_type,
        )
        for child_chunk in _chunk_document_fixed(section_document, section, chunk_size, overlap):
            chunks.append(
                ChunkRecord(
                    source_path=child_chunk.source_path,
                    title=child_chunk.title,
                    file_type=child_chunk.file_type,
                    chunk_index=chunk_index,
                    text=child_chunk.text,
                )
            )
            chunk_index += 1
    return chunks


def _split_into_sections(text: str) -> list[str]:
    sections: list[str] = []
    current_lines: list[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if current_lines and _is_heading_line(stripped):
            sections.append("\n".join(current_lines))
            current_lines = [stripped]
            continue
        current_lines.append(stripped)
    if current_lines:
        sections.append("\n".join(current_lines))
    return sections


def _is_heading_line(line: str) -> bool:
    if line.startswith("#"):
        return True
    if line.startswith(("##", "###")):
        return True
    if len(line) > 80:
        return False
    if line.endswith(":") and len(line) <= 60:
        return True
    if _looks_like_numbered_heading(line):
        return True
    if line.lower().startswith(("purpose", "context", "scope", "preconditions", "verification", "rollback", "trigger ", "review ", "flow ", "signal ", "expected ")):
        return True
    words = line.split()
    if 1 <= len(words) <= 6 and not any(char in line for char in ".。!?！？"):
        alpha_count = sum(1 for char in line if char.isalpha())
        digit_count = sum(1 for char in line if char.isdigit())
        return alpha_count + digit_count >= max(4, len(line) // 2)
    return False


def _looks_like_numbered_heading(line: str) -> bool:
    prefixes = ("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.")
    return any(line.startswith(prefix) for prefix in prefixes)


def normalize_text(text: str) -> str:
    collapsed_lines = (line.strip() for line in text.replace("\r\n", "\n").split("\n"))
    return "\n".join(line for line in collapsed_lines if line)
