from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Iterator, Optional
import os
from langchain_core.documents import Document as LCDocument


@dataclass
class Document:
    """
    Standard Document schema independent of LangChain.
    Matches LangChain's Document structure (page_content & metadata).
    """
    page_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_langchain_document(self):
        """Optional conversion helper for LangChain integration."""
        try:
            
            return LCDocument(page_content=self.page_content, metadata=self.metadata)
        except ImportError:
            raise ImportError(
                "langchain-core is required to convert to a LangChain Document. "
                "Please install `langchain-core` or `langchain`."
            )


class BaseDocumentLoader(ABC):
    """
    Abstract Base Document Loader.
    Follows LangChain BaseLoader design pattern while staying zero-dependency.
    """

    @abstractmethod
    def load(self) -> List[Document]:
        """Load data into Document objects synchronously."""
        pass

    def lazy_load(self) -> Iterator[Document]:
        """Lazy load documents as a generator."""
        yield from self.load()


class DocumentLoader(BaseDocumentLoader):
    """
    General Document Loader that routes to appropriate file parsers
    based on file extension.
    """

    def __init__(self, file_path: str, encoding: str = "utf-8"):
        self.file_path = file_path
        self.encoding = encoding

    def load(self) -> List[Document]:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found at path: {self.file_path}")

        ext = os.path.splitext(self.file_path)[1].lower()

        if ext in [".txt", ".md", ".markdown", ".json", ".csv"]:
            return self._load_text()
        elif ext == ".pdf":
            return self._load_pdf()
        else:
            # Fallback to plain text load attempt
            return self._load_text()

    def _load_text(self) -> List[Document]:
        with open(self.file_path, "r", encoding=self.encoding, errors="ignore") as f:
            content = f.read()

        metadata = {
            "source": self.file_path,
            "filename": os.path.basename(self.file_path),
            "file_type": os.path.splitext(self.file_path)[1],
        }

        return [Document(page_content=content, metadata=metadata)]

    def _load_pdf(self) -> List[Document]:
        try:
            import pypdf
            reader = pypdf.PdfReader(self.file_path)
            documents = []
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                metadata = {
                    "source": self.file_path,
                    "filename": os.path.basename(self.file_path),
                    "page": idx + 1,
                    "total_pages": len(reader.pages),
                }
                documents.append(Document(page_content=text, metadata=metadata))
            return documents
        except ImportError:
            raise ImportError(
                "pypdf is required to parse PDF files natively. "
                "Install it using `pip install pypdf` or `uv add pypdf`."
            )
