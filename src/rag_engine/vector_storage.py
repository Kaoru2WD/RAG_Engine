import json
import math
import sqlite3
from pathlib import Path

from rag_engine.models import ChunkRecord, RetrievalHit


SCHEMA = """
CREATE TABLE IF NOT EXISTS vector_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_path TEXT NOT NULL,
    title TEXT NOT NULL,
    file_type TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    embedding_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vector_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


class VectorIndexStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(SCHEMA)

    def reset(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                DELETE FROM vector_chunks;
                DELETE FROM vector_meta;
                """
            )

    def add_chunks(
        self,
        chunks: list[ChunkRecord],
        embeddings: list[list[float]],
        provider_name: str,
        provider_detail: str,
        document_text_mode: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> int:
        if not chunks:
            return 0
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")

        with self._connect() as connection:
            rows = [
                (
                    chunk.source_path,
                    chunk.title,
                    chunk.file_type,
                    chunk.chunk_index,
                    chunk.text,
                    json.dumps(embedding, ensure_ascii=False),
                )
                for chunk, embedding in zip(chunks, embeddings)
            ]
            connection.executemany(
                """
                INSERT INTO vector_chunks (source_path, title, file_type, chunk_index, text, embedding_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            connection.executemany(
                """
                INSERT INTO vector_meta (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
                """,
                [
                    ("provider_name", provider_name),
                    ("provider_detail", provider_detail),
                    ("document_text_mode", document_text_mode),
                    ("chunk_size", str(chunk_size)),
                    ("chunk_overlap", str(chunk_overlap)),
                    ("chunk_count", str(self.count_chunks(connection))),
                ],
            )
            return len(rows)

    def search(self, query_embedding: list[float], top_k: int) -> list[RetrievalHit]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, source_path, title, file_type, chunk_index, text, embedding_json
                FROM vector_chunks
                """
            ).fetchall()

        scored_rows: list[tuple[float, sqlite3.Row]] = []
        for row in rows:
            embedding = json.loads(row["embedding_json"])
            score = _cosine_similarity(query_embedding, [float(value) for value in embedding])
            if score > 0.0:
                scored_rows.append((score, row))

        scored_rows.sort(key=lambda item: item[0], reverse=True)
        return [
            RetrievalHit(
                chunk_id=row["id"],
                source_path=row["source_path"],
                title=row["title"],
                file_type=row["file_type"],
                chunk_index=row["chunk_index"],
                score=score,
                text=row["text"],
            )
            for score, row in scored_rows[:top_k]
        ]

    def metadata(self) -> dict[str, str]:
        with self._connect() as connection:
            rows = connection.execute("SELECT key, value FROM vector_meta").fetchall()
        return {str(row["key"]): str(row["value"]) for row in rows}

    def count_chunks(self, connection: sqlite3.Connection | None = None) -> int:
        if connection is not None:
            row = connection.execute("SELECT COUNT(*) AS count FROM vector_chunks").fetchone()
            return int(row["count"])
        with self._connect() as local_connection:
            row = local_connection.execute("SELECT COUNT(*) AS count FROM vector_chunks").fetchone()
            return int(row["count"])


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("embedding dimensions do not match")
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return numerator / (left_norm * right_norm)
