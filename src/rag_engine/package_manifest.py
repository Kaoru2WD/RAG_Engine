import json
from dataclasses import asdict
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


EngineMode = Literal["inline_bm25", "vector", "hybrid"]
PackageChannel = Literal["company", "team-beta", "local", "archive"]


class ReleaseManifest(BaseModel):
    package_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    channel: PackageChannel
    version: str = Field(min_length=1)
    built_at: str = Field(min_length=1)
    package_hash: str = Field(min_length=1)
    data_hash: str = Field(min_length=1)
    download_url: str | HttpUrl
    entrypoint: str = Field(min_length=1)
    engine_modes: list[EngineMode] = Field(min_length=1)
    source: str = Field(min_length=1)
    release_notes: list[str] = Field(default_factory=list)
    minimum_runtime: str = Field(default="static-browser")


class InstalledPackageRecord(BaseModel):
    package_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    channel: PackageChannel
    version: str = Field(min_length=1)
    installed_at: str = Field(min_length=1)
    package_hash: str = Field(min_length=1)
    install_root: str = Field(min_length=1)
    entrypoint: str = Field(min_length=1)
    engine_modes: list[EngineMode] = Field(min_length=1)
    source_manifest_url: str | HttpUrl | None = None


class LauncherRegistry(BaseModel):
    packages: list[InstalledPackageRecord] = Field(default_factory=list)


def write_release_manifest(path: Path, manifest: ReleaseManifest) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def write_launcher_registry(path: Path, registry: LauncherRegistry) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
