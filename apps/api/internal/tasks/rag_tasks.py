from internal.services.router_service import RouterService
from internal.models import DocumentVector
from internal.rag.embeddings import OpenAIEmbeddingProvider
from internal.rag.embeddings import EmbeddingFactory
from internal.rag.embeddings import EmbeddingModelConfig
from internal.rag.chunking.chunking import RecursiveChunker
import os
import tempfile
from internal.models import UploadedDocument
from internal.core.db import SessionLocal
from internal.services.celery_app import celery_app
from internal.services.aws_service import download_file_from_s3
from internal.rag.loaders.documentLoader import DocumentLoader
from kombu import Queue
from requests.exceptions import RequestException

celery_app.conf.task_queues = (
    Queue("rag"),
)

celery_app.conf.task_default_queue = "rag"

celery_app.conf.worker_prefetch_multiplier = 1


@celery_app.task(
    queue="rag",
    retry_backoff=3, 
    max_retries=2, 
    retry_backoff_max=600,
    autoretry_for=(RequestException,),
    acks_late=True,        # ✅ confirm after execution
    acks_on_failure=False, # ❌ don't confirm if failed
    store_errors=True      # ✅ store exception in result
)
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
            recursive_chunker = RecursiveChunker(chunk_size=1000,chunk_overlap=200)
            chunked_doc = recursive_chunker.chunk(documents)
           
        #    extract text from chunked document
            texts = [doc.page_content for doc in chunked_doc]
            print("texts: ",len(texts))
           
        #    embedding generation
            # Configuration for embeddings
            embed_provider = EmbeddingFactory.get_provider("openai")

            # Generate embeddings for the texts
            embeddings = embed_provider.embed_documents(texts)

            print(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}")

            vector_records =[]
            for chunk , embedding in zip(chunked_doc, embeddings):
                chunk_meta = dict(chunk.metadata) if hasattr(chunk, "metadata") and chunk.metadata else {}
                chunk_meta["document_id"] = doc.id
                doc_vector = DocumentVector(
                    document_id=doc.id,
                    title=doc.title,
                    content=chunk.page_content,
                    doc_metadata=chunk_meta,
                    embedding=embedding
                )

                vector_records.append(doc_vector)
            
            db.add_all(vector_records)
            db.commit()
        # -------------------------------------------------
            doc.status = "COMPLETED"
            db.commit()
        finally:
            # Always clean up the temporary file from local disk
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    except Exception as e:
        db.rollback()
        if 'doc' in locals() and doc:
            doc.status = "FAILED"
            doc.processing_error = str(e)
            db.commit()
        print(f"Error in ingestion pipeline: {e}")
    finally:
        db.close()
    
    

def query_processing(
    query_text:str,
    top_k:int = 20,
    
    
)->dict:
    db = SessionLocal() 
    try:
        # Embed user query
        embed_provider = EmbeddingFactory.get_provider("openai")
        query_vector = embed_provider.embed_query(query_text)
        router_service = RouterService()
        doc_id = router_service.route_query_to_document(query_text, db)
        if doc_id is None:
            return {"answer": "No relevant document found for the given query.", "sources": []}

        # search nearest chunks using pgvector cosine distance
        query = db.query(DocumentVector).filter(DocumentVector.doc_metadata["document_id"].as_integer()==doc_id)
        if doc_id:
            query = query.filter(DocumentVector.doc_metadata["document_id"].as_integer()==doc_id)
            relevant_chunks = (query.order_by(DocumentVector.embedding.cosime_distance(query_vector)).limit(top_k).all())
        if not relevant_chunks:
            return {"answer": "No relevant chunks found for the given query.", "sources": []}

        context_str = "\n\n---\n\n".join([f"[Title:{chunk.title}]\n{chunk.content}" for chunk in relevant_chunks])
        #  4. Generate answer via LLM (e.g. ChatOpenAI, Gemini, or OpenRouter)

        prompt = f"Context:\n{context_str}\n\nQuestion: {query_text}"
        response = llm.invoke(prompt)
        return {
            "query": query_text,
            "context": context_str,
            "sources": [
                {
                    "id": chunk.id,
                    "title": chunk.title,
                    "metadata": chunk.doc_metadata
                }
                for chunk in relevant_chunks
            ]
        }
    finally:
        db.close()

    