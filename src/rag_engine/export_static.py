import argparse
import hashlib
import json
from pathlib import Path

from rag_engine.chunking import chunk_document
from rag_engine.config import settings
from rag_engine.extractors import discover_documents, extract_document
from rag_engine.redaction import apply_placeholders, load_placeholder_rules
from rag_engine.text_processing import build_search_text


def load_evaluation_cases(documents_dir: Path) -> list[dict]:
    evaluation_path = documents_dir / "evaluation_cases.json"
    if not evaluation_path.exists():
        return []
    return json.loads(evaluation_path.read_text(encoding="utf-8"))


def build_static_index(documents_dir: Path, placeholder_path: Path | None = None) -> tuple[dict, dict]:
    rules = load_placeholder_rules(placeholder_path)
    evaluation_cases = load_evaluation_cases(documents_dir)
    documents = []
    chunks = []
    dry_run_documents = []
    dry_run_chunks = []

    for document_number, path in enumerate(discover_documents(documents_dir), start=1):
        document = extract_document(path)
        document_chunks = chunk_document(document, settings.chunk_size, settings.chunk_overlap)
        document_ref = f"DOC-{document_number:03d}"
        safe_title, title_keys = apply_placeholders(document.title, rules)
        safe_path, path_keys = apply_placeholders(str(path.relative_to(documents_dir)), rules)

        documents.append(
            {
                "document_ref": document_ref,
                "source_label": safe_path,
                "source_url": path.resolve().as_uri(),
                "title": safe_title,
                "file_type": document.file_type,
                "placeholder_keys": sorted(set(title_keys + path_keys)),
                "chunk_count": len(document_chunks),
            }
        )
        dry_run_documents.append(
            {
                "document_ref": document_ref,
                "file_type": document.file_type,
                "chunk_count": len(document_chunks),
                "raw_title_sha256": _sha256(document.title),
                "raw_path_sha256": _sha256(str(path)),
            }
        )

        for chunk in document_chunks:
            redacted_text, matched_keys = apply_placeholders(chunk.text, rules)
            tokens = build_search_text(redacted_text).split()
            chunk_ref = f"{document_ref}-C{chunk.chunk_index:03d}"
            chunks.append(
                {
                    "id": len(chunks),
                    "chunk_ref": chunk_ref,
                    "document_ref": document_ref,
                    "source_label": safe_path,
                    "source_url": path.resolve().as_uri(),
                    "title": safe_title,
                    "file_type": chunk.file_type,
                    "chunk_index": chunk.chunk_index,
                    "text": redacted_text,
                    "tokens": tokens,
                    "token_count": len(tokens),
                    "placeholder_keys": matched_keys,
                }
            )
            dry_run_chunks.append(
                {
                    "chunk_ref": chunk_ref,
                    "document_ref": document_ref,
                    "raw_char_count": len(chunk.text),
                    "raw_sha256": _sha256(chunk.text),
                    "placeholder_keys": matched_keys,
                    "token_count_after_redaction": len(tokens),
                }
            )

    payload = {
        "meta": {
            "documents_dir": str(documents_dir),
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
            "document_count": len(documents),
            "chunk_count": len(chunks),
            "placeholder_catalog": [
                {"key": rule.key, "placeholder": rule.placeholder}
                for rule in rules
            ],
            "operator_help": [
                {"syntax": "+term", "meaning": "必須語"},
                {"syntax": "-term", "meaning": "除外語"},
                {"syntax": "\"phrase\"", "meaning": "フレーズ一致"},
                {"syntax": "source:value", "meaning": "出典ラベル絞り込み"},
                {"syntax": "title:value", "meaning": "タイトル絞り込み"},
            ],
            "evaluation_cases": evaluation_cases,
        },
        "documents": documents,
        "chunks": chunks,
    }
    dry_run = {
        "meta": {
            "documents_dir": str(documents_dir),
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
            "document_count": len(documents),
            "chunk_count": len(chunks),
            "placeholder_rule_count": len(rules),
            "note": "Raw chunk text is not persisted. This report stores only hashes and counts.",
        },
        "documents": dry_run_documents,
        "chunks": dry_run_chunks,
    }
    return payload, dry_run


def write_static_index(output_path: Path, documents_dir: Path, placeholder_path: Path | None = None) -> Path:
    payload, _ = build_static_index(documents_dir, placeholder_path=placeholder_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    js = "window.SEARCH_DATA = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n"
    output_path.write_text(js, encoding="utf-8")
    return output_path


def write_dry_run_report(output_path: Path, documents_dir: Path, placeholder_path: Path | None = None) -> Path:
    _, dry_run = build_static_index(documents_dir, placeholder_path=placeholder_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(dry_run, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build dry-run chunk report and sanitized static search data.")
    parser.add_argument("--documents-dir", type=Path, default=settings.documents_dir)
    parser.add_argument("--output", type=Path, default=Path("web/search-data.js"))
    parser.add_argument("--dry-run-output", type=Path, default=settings.dry_run_report_path)
    parser.add_argument("--placeholder-rules", type=Path, default=settings.placeholder_rules_path)
    args = parser.parse_args()

    dry_run_path = write_dry_run_report(
        output_path=args.dry_run_output,
        documents_dir=args.documents_dir,
        placeholder_path=args.placeholder_rules,
    )
    export_path = write_static_index(
        output_path=args.output,
        documents_dir=args.documents_dir,
        placeholder_path=args.placeholder_rules,
    )
    print(dry_run_path)
    print(export_path)


if __name__ == "__main__":
    main()
