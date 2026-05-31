from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from rag_engine.runtime_paths import (
    default_database_path,
    default_documents_dir,
    default_dry_run_report_path,
    default_placeholder_rules_path,
    default_vector_database_path,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAG_ENGINE_", env_file=".env", extra="ignore")

    app_name: str = "HILS RAG Portfolio"
    documents_dir: Path = Field(default_factory=default_documents_dir)
    database_path: Path = Field(default_factory=default_database_path)
    vector_database_path: Path = Field(default_factory=default_vector_database_path)
    chunk_size: int = 800
    chunk_overlap: int = 100
    chunk_strategy: str = "fixed"
    vector_chunk_size: int = 800
    vector_chunk_overlap: int = 100
    vector_chunk_strategy: str = "fixed"
    default_top_k: int = 3
    placeholder_rules_path: Path = Field(default_factory=default_placeholder_rules_path)
    dry_run_report_path: Path = Field(default_factory=default_dry_run_report_path)
    forms_request_url: str | None = None
    vector_embedding_provider: str = "auto"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_embedding_model: str = "nomic-embed-text"
    local_vector_dimensions: int = 512
    vector_document_text_mode: str = "title_source_text"
    hybrid_backend_url: str | None = "http://127.0.0.1:8000/backend/query"
    hybrid_backend_timeout_seconds: float = 20.0


settings = Settings()
