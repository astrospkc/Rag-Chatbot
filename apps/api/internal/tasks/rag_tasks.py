import os
import tempfile
from internal.models import UploadedDocument
from internal.core.db import SessionLocal
from internal.services.celery_app import celery_app
from internal.services.aws_service import download_file_from_s3
from internal.rag.loaders.documentLoader import DocumentLoader
from kombu import Queue

celery_app.conf.task_queues = (
    Queue("rag"),
)

celery_app.conf.task_default_queue = "rag"

celery_app.conf.worker_prefetch_multiplier = 1


@celery_app.task(queue="rag")
def run_ingestion_pipeline(file_id: int):
    print("Processing file ID:", file_id)
    
    db = SessionLocal()
    try:
        doc = db.query(UploadedDocument).filter(UploadedDocument.id == file_id).first()
        if not doc:
            print(f"Document with ID {file_id} not found.")
            return

        # Update status to PROCESSING
        doc.status = "PROCESSING"
        db.commit()
        
        # 1. Create a local temporary file with the same file extension
        ext = os.path.splitext(doc.original_filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            temp_file_path = temp_file.name

        # 2. Download from S3 to temp local file
        success = download_file_from_s3(doc.original_filename, temp_file_path)
        if not success:
            doc.status = "FAILED"
            doc.processing_error = "Failed to download document from S3"
            db.commit()
            return

        try:
            # 3. Load document using DocumentLoader
            document_loader = DocumentLoader(temp_file_path)
            documents = document_loader.load()
            print(f"Successfully loaded {len(documents)} document pages/chunks from S3.")

            # 4. Next steps: Chunking -> Embedding generation -> Store in DB (embeded_documents)
            
            doc.status = "COMPLETED"
            db.commit()
        finally:
            # Always clean up the temporary file from local disk
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    except Exception as e:
        if 'doc' in locals() and doc:
            doc.status = "FAILED"
            doc.processing_error = str(e)
            db.commit()
        print(f"Error in ingestion pipeline: {e}")
    finally:
        db.close()
    
    


#    filepath = "/home/punam/Documents/punam_2/punam/punam/ai_projects/new_ai_projects/rag_chatbot/apps/api/telepsychics-pdfdrive-.pdf"

#     # this will be done later-----
#     # # Trigger background ingestion task for testing
#     # background_tasks.add_task(
#     #     ingestion_pipeline.run,
#     #     filepath
#     # )

#     # 1. pdf will be loaded
#     # 2. chunking 
#     # 3. embedding generation
#     # 4. embedding + text will be saved in postgres db
#     # 5. vector store
#     # 6. FAISS index will be created 

#     # pdf loader
#     document_loader = DocumentLoader(filepath)
#     document = document_loader.load()

#     # print("pdf document load: ", document)
    
#     recursive_chunker = RecursiveChunker(chunk_size=1000, chunk_overlap=200)
#     chunked_documents = recursive_chunker.chunk(document)
#     # chunked_documents = recursive_chunker.chunk_list(document, chunk_size=100)

    
#     # extract page contents
#     texts = [doc.page_content for doc in chunked_documents]
#     print("texts: ",len(texts))
#     # print("text: ", texts[0])
