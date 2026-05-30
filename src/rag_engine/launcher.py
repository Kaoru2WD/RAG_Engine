import argparse
import os
import socket
import sqlite3
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

import uvicorn

from rag_engine.runtime_paths import bundle_root, default_database_path, default_vector_database_path, package_data_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch the HILS RAG UI as a local packaged app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--smoke-test", action="store_true")
    parser.add_argument("--startup-timeout", type=float, default=30.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    port = choose_port(args.host, args.port)
    os.environ["RAG_ENGINE_HYBRID_BACKEND_URL"] = f"http://{args.host}:{port}/backend/query"
    seed_bundled_databases()
    ensure_local_indexes()
    from rag_engine.main import create_app

    server = uvicorn.Server(
        uvicorn.Config(
            create_app(),
            host=args.host,
            port=port,
            reload=False,
            log_level="info",
        )
    )

    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    health_url = f"http://{args.host}:{port}/health"
    wait_for_health(health_url, args.startup_timeout)

    if args.smoke_test:
        server.should_exit = True
        server_thread.join(timeout=5.0)
        return 0

    ui_url = f"http://{args.host}:{port}/ui"
    print(f"HILS RAG UI: {ui_url}")
    print("Press Ctrl+C to stop the local server.")
    if not args.no_browser:
        webbrowser.open(ui_url, new=1)

    try:
        while server_thread.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Stopping HILS RAG UI...")
    finally:
        server.should_exit = True
        server_thread.join(timeout=10.0)
    return 0


def choose_port(host: str, preferred_port: int) -> int:
    for offset in range(20):
        port = preferred_port + offset
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.3)
            if sock.connect_ex((host, port)) != 0:
                return port
    raise RuntimeError(f"No available port found near {preferred_port}.")


def wait_for_health(health_url: str, startup_timeout: float) -> None:
    deadline = time.time() + startup_timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(health_url, timeout=2.0) as response:
                if response.status == 200:
                    return
        except Exception as exc:  # pragma: no cover - exercised by smoke test
            last_error = exc
            time.sleep(0.5)
    raise RuntimeError(f"Failed to reach {health_url} within {startup_timeout:.1f} seconds.") from last_error


def seed_bundled_databases() -> None:
    source_data_dir = bundle_root() / "data"
    if not source_data_dir.exists():
        return

    target_data_dir = package_data_dir()
    target_data_dir.mkdir(parents=True, exist_ok=True)
    for file_name in ("rag_index.sqlite3", "rag_vector.sqlite3"):
        source_path = source_data_dir / file_name
        target_path = target_data_dir / file_name
        if source_path.exists() and not target_path.exists():
            target_path.write_bytes(source_path.read_bytes())


def ensure_local_indexes() -> None:
    from rag_engine.config import settings
    from rag_engine.service import RagService

    needs_bm25 = not has_chunk_rows(settings.database_path, "chunks")
    needs_vector = not has_chunk_rows(settings.vector_database_path, "vector_chunks")
    if not needs_bm25 and not needs_vector:
        return

    service = RagService(settings)
    if needs_bm25:
        service.rebuild_index()
    if needs_vector:
        service.rebuild_vector_index()


def has_chunk_rows(database_path: Path, table_name: str) -> bool:
    if not database_path.exists():
        return False
    try:
        with sqlite3.connect(database_path) as connection:
            row = connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
    except sqlite3.Error:
        return False
    return bool(row and int(row[0]) > 0)


if __name__ == "__main__":
    raise SystemExit(main())
