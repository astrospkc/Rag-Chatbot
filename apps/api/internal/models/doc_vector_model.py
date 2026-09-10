from sqlalchemy import Column, Integer, Text, DateTime, Index, ForeignKey,func
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from internal.core.db import Base
from sqlalchemy.orm import relationship


class DocumentVector(Base):
    __tablename__ = "embeded_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("uploaded_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    doc_metadata = Column("metadata", JSONB, server_default="{}")
    embedding = Column(Vector(768), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    document = relationship("UploadedDocument", back_populates="vectors")
    __table_args__ = (
        Index(
            "embeded_documents_embedding_hnsw_idx",
            embedding,
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    def __repr__(self):
        return f"<DocumentVector(id={self.id}, title='{self.title}')>"
