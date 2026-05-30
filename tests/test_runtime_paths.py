from pathlib import Path

from rag_engine import runtime_paths


def test_resolve_web_dir_in_repo_mode() -> None:
    expected = Path("web").resolve()
    assert runtime_paths.resolve_web_dir() == expected


def test_default_database_path_in_repo_mode() -> None:
    assert runtime_paths.default_database_path() == Path("data/rag_index.sqlite3")
