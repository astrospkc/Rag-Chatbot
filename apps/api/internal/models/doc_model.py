from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime, func
from internal.core.db import Base
from sqlalchemy.orm import relationship


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    original_filename = Column(Text, nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(BigInteger, nullable=True)
    status = Column(String(50), nullable=False, default="PENDING", index=True)
    processing_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


    vectors = relationship("DocumentVector", back_populates="document", cascade="all, delete-orphan")
    def __repr__(self):
        return f"<UploadedDocument(id={self.id}, title='{self.title}', status='{self.status}')>"
