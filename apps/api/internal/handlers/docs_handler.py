
from internal.services.router_service import RouterService
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
from internal.tasks.rag_tasks import query_processing
from fastapi import APIRouter, UploadFile, Form, File, Depends
from sqlalchemy.orm import Session
from internal.core.db import get_db
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

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

class QueryRequest(BaseModel):
    user_query:str

router_service = RouterService()

@router.post("/query/stream")
async def query_document(requests:QueryRequest, db:Session = Depends(get_db)):
    user_query = requests.user_query
    print("Received user query: ", user_query)
    result = query_processing(user_query)
    return result


class RetryDocRequest(BaseModel):
    file_id: int


@router.post("/doc/retry")
def embed_failed_document(request: RetryDocRequest, db: Session = Depends(get_db)):
    file_id = request.file_id
    print(f"Received request to retry embedding for document ID: {file_id}")
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == file_id).first()
    print(f"Retrying embedding for document ID: {file_id}, Document: {doc}")
    if not doc:
        return {
            "message": "Document not found",
            "status": "error"
        }
    if doc.status == "FAILED":
        return {
            "message": "Document is in FAILED status",
            "status": "error"
        }
    # Re-run the ingestion pipeline for the failed document
    run_ingestion_pipeline.delay(file_id)
    return {
        "message": f"Re-ingestion of document {doc.id} has been queued.",
        "status": "processing"
    }