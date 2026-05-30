from rag_engine.embedding_provider import BaseEmbeddingProvider
from rag_engine.models import RetrievalHit
from rag_engine.vector_storage import VectorIndexStore


class VectorRetriever:
    def __init__(self, store: VectorIndexStore, embedding_provider: BaseEmbeddingProvider) -> None:
        self.store = store
        self.embedding_provider = embedding_provider

    def retrieve(self, question: str, top_k: int) -> list[RetrievalHit]:
        embedding = self.embedding_provider.embed_query(question)
        return self.store.search(embedding, top_k)
