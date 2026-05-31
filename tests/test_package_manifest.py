import json
from pathlib import Path

from rag_engine.build_release_manifest import build_manifest
from rag_engine.package_manifest import LauncherRegistry, ReleaseManifest, write_launcher_registry, write_release_manifest


def test_build_manifest_hashes_files(tmp_path: Path) -> None:
    package_path = tmp_path / "package.zip"
    data_path = tmp_path / "search-data.js"
    package_path.write_bytes(b"package")
    data_path.write_text("window.SEARCH_DATA = {};\n", encoding="utf-8")

    manifest = build_manifest(
        package_id="hils-procedure-rag",
        display_name="HILS Procedure Search",
        channel="company",
        version="2026.05.31-01",
        package_path=package_path,
        data_path=data_path,
        download_url="./releases/rag-ui.zip",
        entrypoint="index.html",
        engine_modes=["inline_bm25", "vector"],
        source="Kaoru2WD/RAG_Engine",
        release_notes=["note"],
        forms_request_url="https://example.com/forms/request",
    )

    assert manifest.package_hash.startswith("sha256:")
    assert manifest.data_hash.startswith("sha256:")
    assert manifest.forms_request_url == "https://example.com/forms/request"


def test_write_release_manifest_roundtrips(tmp_path: Path) -> None:
    manifest = ReleaseManifest(
        package_id="hils-procedure-rag",
        display_name="HILS Procedure Search",
        channel="company",
        version="2026.05.31-01",
        built_at="2026-05-31T10:00:00+09:00",
        package_hash="sha256:a",
        data_hash="sha256:b",
        download_url="./releases/rag-ui.zip",
        entrypoint="index.html",
        engine_modes=["inline_bm25"],
        source="Kaoru2WD/RAG_Engine",
        forms_request_url="https://example.com/forms/request",
    )
    path = write_release_manifest(tmp_path / "latest-manifest.json", manifest)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["package_id"] == "hils-procedure-rag"


def test_write_launcher_registry_roundtrips(tmp_path: Path) -> None:
    registry = LauncherRegistry.model_validate(
        {
            "packages": [
                {
                    "package_id": "local-sandbox-rag",
                    "display_name": "Local Sandbox",
                    "channel": "local",
                    "version": "2026.05.31-dev",
                    "installed_at": "2026-05-31T10:10:00+09:00",
                    "package_hash": "sha256:x",
                    "install_root": "C:/temp",
                    "entrypoint": "index.html",
                    "engine_modes": ["inline_bm25"],
                }
            ]
        }
    )
    path = write_launcher_registry(tmp_path / "launcher-registry.json", registry)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["packages"][0]["channel"] == "local"
