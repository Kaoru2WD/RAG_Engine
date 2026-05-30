import sqlite3
from pathlib import Path

from rag_engine.models import ChunkRecord, RetrievalHit
from rag_engine.text_processing import build_search_text


SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_path TEXT NOT NULL,
    title TEXT NOT NULL,
    file_type TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    text,
    title,
    source_path,
    content='chunks',
    content_rowid='id'
);
"""


class IndexStore:
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
                DELETE FROM chunks;
                DELETE FROM chunks_fts;
                """
            )

    def add_chunks(self, chunks: list[ChunkRecord]) -> int:
        if not chunks:
            return 0
        with self._connect() as connection:
            rows = [
                (chunk.source_path, chunk.title, chunk.file_type, chunk.chunk_index, chunk.text)
                for chunk in chunks
            ]
            for chunk_row, chunk in zip(rows, chunks):
                cursor = connection.execute(
                    """
                    INSERT INTO chunks (source_path, title, file_type, chunk_index, text)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    chunk_row,
                )
                row_id = int(cursor.lastrowid)
                connection.execute(
                    """
                    INSERT INTO chunks_fts (rowid, text, title, source_path)
                    VALUES (?, ?, ?, ?)
                    """,
                    (row_id, build_search_text(chunk.text), chunk.title, chunk.source_path),
                )
            return len(rows)

    def search(self, query: str, top_k: int) -> list[RetrievalHit]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    chunks.id,
                    chunks.source_path,
                    chunks.title,
                    chunks.file_type,
                    chunks.chunk_index,
                    chunks.text,
                    bm25(chunks_fts) AS score
                FROM chunks_fts
                JOIN chunks ON chunks.id = chunks_fts.rowid
                WHERE chunks_fts MATCH ?
                ORDER BY score
                LIMIT ?
                """,
                (query, top_k),
            ).fetchall()

        return [
            RetrievalHit(
                chunk_id=row["id"],
                source_path=row["source_path"],
                title=row["title"],
                file_type=row["file_type"],
                chunk_index=row["chunk_index"],
                score=float(row["score"]),
                text=row["text"],
            )
            for row in rows
        ]
