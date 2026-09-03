from abc import ABC, abstractmethod
from typing import List, Any, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

try:
    from langchain_experimental.text_splitter import SemanticChunker as LCSemanticChunker
except ImportError:
    LCSemanticChunker = None


class BaseChunker(ABC):
    """
    Abstract base class for chunking documents.
    """

    @abstractmethod
    def chunk(self, documents: List[Document]) -> List[Document]:
        """
        Split a list of LangChain documents into smaller chunks.
        """
        pass
    

    def chunk_list(self, data:list, chunk_size: int=100):
        for i in range(0, len(data), chunk_size):
            yield data[i : i+ chunk_size]


class LangChainChunkerAdapter(BaseChunker):
    """
    Adapter class to wrap any LangChain TextSplitter inside BaseChunker.
    """

    def __init__(self, text_splitter: Any):
        self.text_splitter = text_splitter

    def chunk(self, documents: List[Document]) -> List[Document]:
        return self.text_splitter.split_documents(documents)


class RecursiveChunker(BaseChunker):
    """
    Recursive Character Text Chunker.
    Splits text recursively by character sets (e.g. paragraph, sentence, word).
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        **kwargs: Any
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs
        )
        self.adapter = LangChainChunkerAdapter(self.splitter)

    def chunk(self, documents: List[Document]) -> List[Document]:
        return self.adapter.chunk(documents)


class SemanticChunker(BaseChunker):
    """
    Semantic Chunker.
    Splits text based on semantic similarity of sentences using an embeddings model.
    """

    def __init__(
        self,
        embeddings: Any,
        breakpoint_threshold_type: str = "percentile",
        **kwargs: Any
    ):
        if LCSemanticChunker is None:
            raise ImportError(
                "langchain_experimental is required for SemanticChunker. "
                "Please install it using `pip install langchain-experimental`."
            )
        self.embeddings = embeddings
        self.splitter = LCSemanticChunker(
            embeddings=embeddings,
            breakpoint_threshold_type=breakpoint_threshold_type,
            **kwargs
        )
        self.adapter = LangChainChunkerAdapter(self.splitter)

    def chunk(self, documents: List[Document]) -> List[Document]:
        return self.adapter.chunk(documents)
