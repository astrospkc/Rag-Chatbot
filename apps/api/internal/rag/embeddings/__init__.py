from internal.rag.embeddings.embeddings import BaseEmbeddingModel, LangChainEmbeddingsAdapter, EmbeddingModelConfig
from internal.rag.embeddings.gemini import GeminiEmbeddingProvider
from internal.rag.embeddings.openai import OpenAIEmbeddingProvider

class EmbeddingFactory:
    """
    Factory class to instantiate embedding providers easily by provider name.
    """

    @staticmethod
    def get_provider(provider_name: str, **kwargs) -> BaseEmbeddingModel:
        provider_name = provider_name.lower().strip()
        if provider_name in ["gemini", "google"]:
            return GeminiEmbeddingProvider(**kwargs)
        elif provider_name in ["openai"]:
            return OpenAIEmbeddingProvider(**kwargs)
        else:
            raise ValueError(f"Unsupported embedding provider: '{provider_name}'")

__all__ = [
    "BaseEmbeddingModel",
    "LangChainEmbeddingsAdapter",
    "EmbeddingModelConfig",
    "GeminiEmbeddingProvider",
    "OpenAIEmbeddingProvider",
    "EmbeddingFactory",
]
