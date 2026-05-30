from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, Field


@dataclass(slots=True)
class DocumentRecord:
    source_path: Path
    content: str
    title: str
    file_type: str


@dataclass(slots=True)
class ChunkRecord:
    source_path: str
    title: str
    file_type: str
    chunk_index: int
    text: str


@dataclass(slots=True)
class RetrievalHit:
    chunk_id: int
    source_path: str
    title: str
    file_type: str
    chunk_index: int
    score: float
    text: str


@dataclass(slots=True)
class SearchHitRecord:
    chunk_id: int | None
    document_ref: str
    source_path: str | None
    source_label: str
    source_url: str
    title: str
    file_type: str
    chunk_index: int
    score: float
    text: str
    placeholder_keys: list[str]


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)
    engine: str | None = None


class QueryResponse(BaseModel):
    question: str
    engine: str
    answer: str
    hits: list[dict]
    backend_status: str | None = None


class RebuildResponse(BaseModel):
    indexed_documents: int
    indexed_chunks: int
    skipped_files: list[str]
    provider_name: str | None = None
    provider_detail: str | None = None
