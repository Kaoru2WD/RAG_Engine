import argparse
from pathlib import Path

import PyInstaller.__main__


def build_exe(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the packaged HILS RAG launcher executable.")
    parser.add_argument("--name", default="HILSRAGLauncher")
    parser.add_argument("--dist-path", default="dist")
    parser.add_argument("--work-path", default="build/pyinstaller")
    parser.add_argument("--spec-path", default="build/spec")
    parser.add_argument("--onefile", action="store_true")
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[2]
    launcher_script = repo_root / "src" / "rag_engine" / "launcher.py"
    build_args = [
        str(launcher_script),
        "--noconfirm",
        "--clean",
        "--name",
        args.name,
        "--distpath",
        str(repo_root / args.dist_path),
        "--workpath",
        str(repo_root / args.work_path),
        "--specpath",
        str(repo_root / args.spec_path),
        "--paths",
        str(repo_root / "src"),
        "--add-data",
        f"{repo_root / 'web'};web",
        "--add-data",
        f"{repo_root / 'hils_rag_sample_docs'};hils_rag_sample_docs",
        "--add-data",
        f"{repo_root / 'placeholder_rules.example.json'};.",
    ]

    data_dir = repo_root / "data"
    if data_dir.exists():
        build_args.extend(["--add-data", f"{data_dir};data"])

    if args.onefile:
        build_args.append("--onefile")
    else:
        build_args.append("--onedir")

    PyInstaller.__main__.run(build_args)
    return 0


if __name__ == "__main__":
    raise SystemExit(build_exe())
