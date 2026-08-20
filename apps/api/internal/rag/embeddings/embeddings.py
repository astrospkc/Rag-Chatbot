from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

try:
    from langchain_core.embeddings import Embeddings as LangChainEmbeddings
except ImportError:
    LangChainEmbeddings = None


@dataclass
class EmbeddingModelConfig:
    model_name: str
    dimensions: Optional[int] = None
    model_kwargs: Dict[str, Any] = field(default_factory=dict)


class BaseEmbeddingModel(ABC):
    """
    Abstract base class for framework-agnostic embedding models.
    Any custom, HuggingFace, OpenAI, or custom API embedding provider can implement this interface.
    """

    @abstractmethod
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Embed a list of documents/texts into vector representations."""
        pass

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """Embed a single query string into a vector representation."""
        pass

    def to_langchain(self) -> "LangChainEmbeddingsAdapter":
        """Wrap this framework-agnostic embedding model into a LangChain-compatible Embeddings object."""
        return LangChainEmbeddingsAdapter(self)


class LangChainEmbeddingsAdapter:
    """
    Adapter class to make any BaseEmbeddingModel fully compatible with LangChain interfaces/vectorstores.
    Inherits dynamically or acts as a proxy for `langchain_core.embeddings.Embeddings`.
    """

    def __init__(self, embedding_model: BaseEmbeddingModel):
        self.embedding_model = embedding_model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embedding_model.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embedding_model.embed_query(text)


if LangChainEmbeddings is not None:
    # Ensure type hierarchy compatibility if langchain_core is installed
    LangChainEmbeddingsAdapter = type(
        "LangChainEmbeddingsAdapter",
        (LangChainEmbeddings,),
        dict(LangChainEmbeddingsAdapter.__dict__),
    )
