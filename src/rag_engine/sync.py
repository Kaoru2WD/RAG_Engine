from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SyncResult:
    copied_files: int
    skipped_files: int


class DocumentSync:
    def sync(self) -> SyncResult:
        raise NotImplementedError


class LocalMirrorSync(DocumentSync):
    def __init__(self, source_dir: Path, target_dir: Path) -> None:
        self.source_dir = source_dir
        self.target_dir = target_dir

    def sync(self) -> SyncResult:
        # 実ポートフォリオではローカルミラーを ingest 起点にする。
        # SharePoint 実接続はこの外側に置き、repo 内では扱わない。
        self.target_dir.mkdir(parents=True, exist_ok=True)
        copied_files = 0
        skipped_files = 0

        for source_path in self.source_dir.rglob("*"):
            if not source_path.is_file():
                continue
            relative = source_path.relative_to(self.source_dir)
            target_path = self.target_dir / relative
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if target_path.exists() and target_path.read_bytes() == source_path.read_bytes():
                skipped_files += 1
                continue
            target_path.write_bytes(source_path.read_bytes())
            copied_files += 1

        return SyncResult(copied_files=copied_files, skipped_files=skipped_files)
