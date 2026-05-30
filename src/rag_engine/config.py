from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAG_ENGINE_", env_file=".env", extra="ignore")

    app_name: str = "HILS RAG Portfolio"
    documents_dir: Path = Field(default=Path("hils_rag_sample_docs"))
    database_path: Path = Field(default=Path("data/rag_index.sqlite3"))
    vector_database_path: Path = Field(default=Path("data/rag_vector.sqlite3"))
    chunk_size: int = 800
    chunk_overlap: int = 100
    vector_chunk_size: int = 800
    vector_chunk_overlap: int = 100
    default_top_k: int = 3
    placeholder_rules_path: Path = Field(default=Path("placeholder_rules.example.json"))
    dry_run_report_path: Path = Field(default=Path("web/chunk-dry-run.json"))
    vector_embedding_provider: str = "auto"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_embedding_model: str = "nomic-embed-text"
    local_vector_dimensions: int = 512
    vector_document_text_mode: str = "title_source_text"
    hybrid_backend_url: str | None = "http://127.0.0.1:8000/backend/query"
    hybrid_backend_timeout_seconds: float = 20.0


settings = Settings()
