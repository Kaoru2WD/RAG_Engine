import hashlib
import math
from dataclasses import dataclass

import httpx

from rag_engine.config import Settings
from rag_engine.text_processing import build_search_text


class EmbeddingProviderError(RuntimeError):
    pass


@dataclass(slots=True)
class EmbeddingBatchResult:
    vectors: list[list[float]]
    provider_name: str
    detail: str


class BaseEmbeddingProvider:
    provider_name = "base"

    def embed_texts(self, texts: list[str]) -> EmbeddingBatchResult:
        raise NotImplementedError

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text]).vectors[0]


class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    provider_name = "ollama"

    def __init__(self, base_url: str, model: str, timeout_seconds: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def embed_texts(self, texts: list[str]) -> EmbeddingBatchResult:
        if not texts:
            return EmbeddingBatchResult(vectors=[], provider_name=self.provider_name, detail=self.model)

        payload = {"model": self.model, "input": texts}
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(f"{self.base_url}/api/embed", json=payload)
            if response.status_code == 501:
                raise EmbeddingProviderError(f"Model '{self.model}' does not expose /api/embed.")
            if response.is_error:
                body = response.text.strip()
                raise EmbeddingProviderError(f"Ollama embed failed ({response.status_code}): {body}")
            data = response.json()

        embeddings = data.get("embeddings")
        if not isinstance(embeddings, list) or not embeddings:
            raise EmbeddingProviderError(f"Ollama embed response is missing embeddings for model '{self.model}'.")

        vectors: list[list[float]] = []
        for item in embeddings:
            if not isinstance(item, list) or not item:
                raise EmbeddingProviderError(f"Ollama returned an invalid embedding vector for model '{self.model}'.")
            vectors.append([float(value) for value in item])
        return EmbeddingBatchResult(vectors=vectors, provider_name=self.provider_name, detail=self.model)


class LocalHashEmbeddingProvider(BaseEmbeddingProvider):
    provider_name = "local-hash"

    def __init__(self, dimensions: int = 512) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        self.dimensions = dimensions

    def embed_texts(self, texts: list[str]) -> EmbeddingBatchResult:
        vectors = [self._embed_one(text) for text in texts]
        return EmbeddingBatchResult(
            vectors=vectors,
            provider_name=self.provider_name,
            detail=f"dimensions={self.dimensions}",
        )

    def _embed_one(self, text: str) -> list[float]:
        normalized = build_search_text(text)
        features = normalized.split()
        compact = normalized.replace(" ", "")
        features.extend(compact[index : index + 3] for index in range(max(len(compact) - 2, 0)))
        vector = [0.0] * self.dimensions
        for feature in features:
            if not feature:
                continue
            digest = hashlib.sha256(feature.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = -1.0 if digest[4] % 2 else 1.0
            weight = 1.0 + min(len(feature), 12) / 12.0
            vector[bucket] += sign * weight
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0.0:
            return vector
        return [value / norm for value in vector]


class AutoEmbeddingProvider(BaseEmbeddingProvider):
    provider_name = "auto"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.ollama_provider = OllamaEmbeddingProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embedding_model,
        )
        self.hash_provider = LocalHashEmbeddingProvider(settings.local_vector_dimensions)
        self.last_detail = "uninitialized"

    def embed_texts(self, texts: list[str]) -> EmbeddingBatchResult:
        try:
            result = self.ollama_provider.embed_texts(texts)
            self.last_detail = result.detail
            return result
        except (EmbeddingProviderError, httpx.HTTPError) as exc:
            result = self.hash_provider.embed_texts(texts)
            result.detail = f"fallback={self.settings.ollama_embedding_model}; reason={exc}"
            self.last_detail = result.detail
            return result


def build_embedding_provider(settings: Settings) -> BaseEmbeddingProvider:
    provider = settings.vector_embedding_provider.lower()
    if provider == "ollama":
        return OllamaEmbeddingProvider(settings.ollama_base_url, settings.ollama_embedding_model)
    if provider == "local-hash":
        return LocalHashEmbeddingProvider(settings.local_vector_dimensions)
    if provider == "auto":
        return AutoEmbeddingProvider(settings)
    raise ValueError(f"Unsupported vector_embedding_provider: {settings.vector_embedding_provider}")
