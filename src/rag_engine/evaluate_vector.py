import json
from pathlib import Path

from rag_engine.config import settings
from rag_engine.service import RagService


def _hit_matches(response_hits: list[dict], expected_labels: set[str], top_k: int) -> bool:
    labels = [hit["source_label"] for hit in response_hits[:top_k]]
    return bool(expected_labels.intersection(labels))


def _top_label(response_hits: list[dict]) -> str | None:
    return response_hits[0]["source_label"] if response_hits else None


def evaluate_cases(cases_path: Path) -> dict:
    dataset = json.loads(cases_path.read_text(encoding="utf-8"))

    bm25_service = RagService(settings)
    bm25_service.rebuild_index()

    vector_conditions = [
        {
            "name": "text_800",
            "vector_document_text_mode": "text",
            "vector_chunk_size": 800,
            "vector_chunk_overlap": 100,
            "vector_chunk_strategy": "fixed",
            "vector_database_path": Path("data/eval_vector_text_800.sqlite3"),
        },
        {
            "name": "title_source_text_800",
            "vector_document_text_mode": "title_source_text",
            "vector_chunk_size": 800,
            "vector_chunk_overlap": 100,
            "vector_chunk_strategy": "fixed",
            "vector_database_path": Path("data/eval_vector_title_source_text_800.sqlite3"),
        },
        {
            "name": "title_source_text_500",
            "vector_document_text_mode": "title_source_text",
            "vector_chunk_size": 500,
            "vector_chunk_overlap": 80,
            "vector_chunk_strategy": "fixed",
            "vector_database_path": Path("data/eval_vector_title_source_text_500.sqlite3"),
        },
        {
            "name": "title_source_text_heading",
            "vector_document_text_mode": "title_source_text",
            "vector_chunk_size": 800,
            "vector_chunk_overlap": 100,
            "vector_chunk_strategy": "heading",
            "vector_database_path": Path("data/eval_vector_title_source_text_heading.sqlite3"),
        },
    ]

    vector_services: dict[str, RagService] = {}
    for condition in vector_conditions:
        experiment_settings = settings.model_copy(update=condition)
        service = RagService(experiment_settings)
        service.rebuild_vector_index()
        vector_services[condition["name"]] = service

    cases_result: list[dict] = []
    summary = {
        "bm25": {"top1": 0, "top3": 0},
        **{condition["name"]: {"top1": 0, "top3": 0} for condition in vector_conditions},
    }

    for row in dataset:
        question = row["question"]
        expected_labels = set(row["expected_source_labels"])
        bm25_response = bm25_service.query(question, top_k=3)
        case_result = {
            "question": question,
            "expected_source_labels": row["expected_source_labels"],
            "bm25": {
                "top1_label": _top_label(bm25_response.hits),
                "top1_hit": _hit_matches(bm25_response.hits, expected_labels, 1),
                "top3_hit": _hit_matches(bm25_response.hits, expected_labels, 3),
            },
            "vectors": {},
        }
        if case_result["bm25"]["top1_hit"]:
            summary["bm25"]["top1"] += 1
        if case_result["bm25"]["top3_hit"]:
            summary["bm25"]["top3"] += 1

        for condition in vector_conditions:
            name = condition["name"]
            response = vector_services[name].query_vector(question, top_k=3)
            top1_hit = _hit_matches(response.hits, expected_labels, 1)
            top3_hit = _hit_matches(response.hits, expected_labels, 3)
            case_result["vectors"][name] = {
                "top1_label": _top_label(response.hits),
                "top1_hit": top1_hit,
                "top3_hit": top3_hit,
            }
            if top1_hit:
                summary[name]["top1"] += 1
            if top3_hit:
                summary[name]["top3"] += 1

        cases_result.append(case_result)

    total = len(dataset) or 1
    aggregate = {
        key: {
            "top1_hit_rate": round(values["top1"] / total, 3),
            "top3_hit_rate": round(values["top3"] / total, 3),
        }
        for key, values in summary.items()
    }

    return {
        "cases_path": str(cases_path),
        "total_cases": len(dataset),
        "aggregate": aggregate,
        "cases": cases_result,
    }


if __name__ == "__main__":
    report = evaluate_cases(Path("hils_rag_sample_docs/evaluation_cases.json"))
    print(json.dumps(report, ensure_ascii=False, indent=2))
