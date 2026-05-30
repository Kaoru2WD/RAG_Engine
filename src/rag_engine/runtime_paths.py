import os
import sys
from pathlib import Path


DEFAULT_PACKAGE_ID = "hils-procedure-rag"


def is_frozen_bundle() -> bool:
    return bool(getattr(sys, "frozen", False))


def bundle_root() -> Path:
    if is_frozen_bundle():
        return Path(getattr(sys, "_MEIPASS")).resolve()
    return Path(__file__).resolve().parents[2]


def package_id() -> str:
    return os.environ.get("RAG_ENGINE_PACKAGE_ID", DEFAULT_PACKAGE_ID)


def package_storage_root() -> Path:
    override_root = os.environ.get("RAG_ENGINE_STORAGE_ROOT")
    if override_root:
        return Path(override_root).expanduser().resolve()
    local_appdata = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return local_appdata / "RAGEngine" / "packages" / package_id()


def package_data_dir() -> Path:
    return package_storage_root() / "data"


def default_documents_dir() -> Path:
    if is_frozen_bundle():
        return bundle_root() / "hils_rag_sample_docs"
    return Path("hils_rag_sample_docs")


def default_database_path() -> Path:
    if is_frozen_bundle():
        return package_data_dir() / "rag_index.sqlite3"
    return Path("data/rag_index.sqlite3")


def default_vector_database_path() -> Path:
    if is_frozen_bundle():
        return package_data_dir() / "rag_vector.sqlite3"
    return Path("data/rag_vector.sqlite3")


def default_placeholder_rules_path() -> Path:
    if is_frozen_bundle():
        return bundle_root() / "placeholder_rules.example.json"
    return Path("placeholder_rules.example.json")


def default_dry_run_report_path() -> Path:
    if is_frozen_bundle():
        return package_storage_root() / "chunk-dry-run.json"
    return Path("web/chunk-dry-run.json")


def resolve_web_dir() -> Path:
    if is_frozen_bundle():
        return bundle_root() / "web"
    return Path("web").resolve()
