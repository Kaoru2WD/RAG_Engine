import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path

from rag_engine.package_manifest import ReleaseManifest, write_release_manifest


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def build_manifest(
    package_id: str,
    display_name: str,
    channel: str,
    version: str,
    package_path: Path,
    data_path: Path,
    download_url: str,
    entrypoint: str,
    engine_modes: list[str],
    source: str,
    release_notes: list[str],
) -> ReleaseManifest:
    built_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    return ReleaseManifest(
        package_id=package_id,
        display_name=display_name,
        channel=channel,
        version=version,
        built_at=built_at,
        package_hash=sha256_file(package_path),
        data_hash=sha256_file(data_path),
        download_url=download_url,
        entrypoint=entrypoint,
        engine_modes=engine_modes,
        source=source,
        release_notes=release_notes,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a package manifest for RAG launcher/exe distribution.")
    parser.add_argument("--package-id", required=True)
    parser.add_argument("--display-name", required=True)
    parser.add_argument("--channel", default="company")
    parser.add_argument("--version", required=True)
    parser.add_argument("--package-path", type=Path, required=True)
    parser.add_argument("--data-path", type=Path, required=True)
    parser.add_argument("--download-url", required=True)
    parser.add_argument("--entrypoint", default="index.html")
    parser.add_argument("--engine-mode", action="append", dest="engine_modes", required=True)
    parser.add_argument("--source", default="Kaoru2WD/RAG_Engine")
    parser.add_argument("--release-note", action="append", default=[])
    parser.add_argument("--output", type=Path, default=Path("web/latest-manifest.json"))
    args = parser.parse_args()

    manifest = build_manifest(
        package_id=args.package_id,
        display_name=args.display_name,
        channel=args.channel,
        version=args.version,
        package_path=args.package_path,
        data_path=args.data_path,
        download_url=args.download_url,
        entrypoint=args.entrypoint,
        engine_modes=args.engine_modes,
        source=args.source,
        release_notes=args.release_note,
    )
    write_release_manifest(args.output, manifest)
    print(args.output)


if __name__ == "__main__":
    main()
