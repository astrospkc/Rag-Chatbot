from time import time
import os
from typing import List, Optional
from internal.rag.embeddings.embeddings import BaseEmbeddingModel


class GeminiEmbeddingProvider(BaseEmbeddingModel):
    """
    Gemini Embedding Provider built using LangChain's GoogleGenerativeAIEmbeddings under the hood.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "models/embedding-001"):
        print("api key :", api_key )
        print("model_name: ", model_name)
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
        except ImportError:
            raise ImportError(
                "langchain-google-genai package is required. Install it using 'pip install langchain-google-genai'."
            )

        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable or api_key parameter is required.")

        self._embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=api_key,
            model=model_name
        )

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        return self._embeddings.embed_documents(documents)

    def embed_query(self, query: str) -> List[float]:
        return self._embeddings.embed_query(query)

    # def embed_documents_with_rate_limit(self,documents: List[str],batch_size: int=5,delay:float=1.0):
    #     embeddings = []
    #     for i in range(0, len(documents), batch_size):
    #         batch_docs = documents[ i : i + batch_size]
    #         batch_embeddings = self._embeddings.embed_documents(batch_docs)
    #         embeddings.extend(batch_embeddings)
    #         if i + batch_size < len(documents):
    #             time.sleep(delay)
    #     return embeddings 
    