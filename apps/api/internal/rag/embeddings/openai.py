import os
from typing import List, Optional
from internal.rag.embeddings.embeddings import BaseEmbeddingModel


class OpenAIEmbeddingProvider(BaseEmbeddingModel):
    """
    OpenAI Embedding Provider built using LangChain's OpenAIEmbeddings under the hood.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "text-embedding-3-small"):
        try:
            from langchain_openai import OpenAIEmbeddings
        except ImportError:
            raise ImportError(
                "langchain-openai package is required. Install it using 'pip install langchain-openai'."
            )

        api_key = api_key or os.getenv("OPENROUTER_ADMIN_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_ADMIN_KEY environment variable or api_key parameter is required.")

        self._embeddings = OpenAIEmbeddings(
            model=model_name,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            check_embedding_ctx_length=False,
            default_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "LangChain RAG"
            }
        )

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        return self._embeddings.embed_documents(documents)

    def embed_query(self, query: str) -> List[float]:
        return self._embeddings.embed_query(query)
