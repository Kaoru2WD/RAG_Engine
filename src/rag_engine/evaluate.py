import json
from pathlib import Path

from rag_engine.config import settings
from rag_engine.service import RagService


def run_evaluation(dataset_path: Path) -> dict[str, float]:
    service = RagService(settings)
    service.rebuild_index()

    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    total = len(dataset)
    top1_hits = 0
    top3_hits = 0

    for row in dataset:
        response = service.query(row["question"], top_k=3)
        hit_sources = [Path(hit["source_path"]).name for hit in response.hits]
        expected_sources = set(row["expected_sources"])

        if hit_sources[:1] and hit_sources[0] in expected_sources:
            top1_hits += 1
        if expected_sources.intersection(hit_sources[:3]):
            top3_hits += 1

    return {
        "top1_hit_rate": top1_hits / total if total else 0.0,
        "top3_hit_rate": top3_hits / total if total else 0.0,
        "questions": float(total),
    }


if __name__ == "__main__":
    metrics = run_evaluation(Path("sample_data/evaluation/questions.json"))
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
