from rag_engine.models import RetrievalHit
from rag_engine.storage import IndexStore
from rag_engine.text_processing import build_query_text


class Retriever:
    def __init__(self, store: IndexStore) -> None:
        self.store = store

    def retrieve(self, question: str, top_k: int) -> list[RetrievalHit]:
        query = build_query_text(question)
        return self.store.search(query, top_k)
