
from internal.models import UploadedDocument
import requests
from typing import Optional
import internal.services.aws_service
from internal.tasks.rag_tasks import run_ingestion_pipeline
from internal.rag.embeddings import EmbeddingModelConfig
from internal.rag.embeddings import EmbeddingFactory
from internal.rag.embeddings.embeddings import LangChainEmbeddingsAdapter
from internal.rag.embeddings.embeddings import LangChainEmbeddings
from internal.rag.chunking.chunking import LangChainChunkerAdapter
from internal.rag.chunking.chunking import RecursiveChunker
from internal.rag.loaders.documentLoader import DocumentLoader
from fastapi import APIRouter, UploadFile, Form, File, Depends
from sqlalchemy.orm import Session
from internal.core.db import get_db

router = APIRouter()


@router.post("/documents")
async def upload_document(
    title: Optional[str] = Form(None),
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    print("file and title: ", file, title)
    
    # 1. Presigned URL for file upload
    response = internal.services.aws_service.create_presigned_post(file.filename)
    print("response: ", response)
    
    file_content = await file.read()
    file_size = len(file_content)
    file_path = f"/tmp/{file.filename}"

    # 2. Upload file content to S3 presigned URL
    files = {'file': (file.filename, file_content)}
    http_response = requests.post(response['url'], data=response['fields'], files=files)

    print(f'File upload HTTP status code: {http_response.status_code}')

    # 3. Store doc in DB if S3 upload succeeded (HTTP 204)
    if http_response.status_code == 204:
        uploaded_doc = UploadedDocument(
            title=title or file.filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            status="PENDING",
        )
        db.add(uploaded_doc)
        db.commit()
        db.refresh(uploaded_doc)
        
        # 4. Queue background ingestion task
        run_ingestion_pipeline.delay(uploaded_doc.id)

    return {
        "message": "Document accepted",
        "status": "processing"
    }
    # background_tasks.add_task(
    #     ingestion_pipeline.run,
    #     file_path
    # )

    return {
        "message": "Document accepted",
        "status": "processing"
    }

@router.get("/documents/{file_id}")
async def get_document_by_id(file_id: int, db: Session = Depends(get_db)):
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == file_id).first()
    if not doc:
        return {
            "message": "Document not found",
            "status": "error"
        }
    return doc

@router.put("/documents/{file_id}")
def update_document(file_id: int, db: Session = Depends(get_db)):
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == file_id).first()
    if not doc:
        return {
            "message": "Document not found",
            "status": "error"
        }
    doc.status = "PROCESSING"
    db.commit()
    return doc