from sqlalchemy.orm import Session

from internal.services.router_service import RouterService
from internal.models import DocumentVector
from internal.rag.embeddings import OpenAIEmbeddingProvider
from internal.rag.embeddings import EmbeddingFactory
from internal.rag.embeddings import EmbeddingModelConfig
from internal.rag.chunking.chunking import RecursiveChunker
from internal.llm.factory import LLMFactory
import os
import tempfile
from internal.models import UploadedDocument
from internal.core.db import SessionLocal
from internal.services.celery_app import celery_app
from internal.services.aws_service import download_file_from_s3
from internal.rag.loaders.documentLoader import DocumentLoader
from internal.services.semantic_caching_service.semantic_cache import SemanticCacheService
from kombu import Queue
from requests.exceptions import RequestException
from fastapi.responses import StreamingResponse

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
    


from internal.core.helper_func.chat_history import (
    get_formatted_guest_history,
    add_guest_chat_turn,
)

semantic_cache = SemanticCacheService()

def query_processing(
    query_text: str,
    session_id: str,
    db: Session,
    user_type: str = "guest",  # "guest" or "employee"
    user_id: str = "guest",
    top_k: int = 20,
) -> dict:
    try:
        llm = LLMFactory.get_llm()

        # 1. Fetch previous conversation history for this session (user_id and session_id are for history)
        chat_history_str = get_formatted_guest_history(session_id) if session_id else ""
        print(f"Session ID: {session_id}, Chat History: {chat_history_str}")

        # 2. Rephrase follow-up query if history exists
        search_query = query_text
        if chat_history_str:
            rephrase_prompt = f"""
            Given the chat history and follow-up question, rewrite it into a standalone search query.
            Do NOT answer the question, only rephrase it. If it is already standalone, return it as is.

            Chat History:
            {chat_history_str}

            Follow-up: {query_text}
            Standalone Query:
            """
            try:
                search_query_response = llm.invoke(rephrase_prompt)

                # Extract text from content or fallback
                raw_text = str(search_query_response.content).strip()

                # If content is empty (e.g. reasoning model put output in reasoning_content)
                if not raw_text and hasattr(search_query_response, "additional_kwargs"):
                    raw_text = search_query_response.additional_kwargs.get("reasoning", "").strip()

                if raw_text:
                    search_query = raw_text
                else:
                    print("LLM returned empty rephrased query. Falling back to original query.")
            except Exception as e:
                print(f"Error during rephrase: {e}. Falling back to original query.")

            print(f"Rephrased '{query_text}' -> '{search_query}'")

        # 3. Generate embedding for search query (used by both Semantic Cache and Vector DB)
        embed_provider = EmbeddingFactory.get_provider("openai")
        query_vector = embed_provider.embed_query(search_query)

        # 4. Check Semantic Cache first (anyone - guest or employee - can access cached data)
        cached_result = None
        try:
            cached_result = semantic_cache.check(
                query_vector=query_vector,
                user_type=user_type
            )
        except Exception as e:
            print(f"[SemanticCache Check Exception]: {e}")

        if cached_result:
            print(f"[CACHE HIT] Returning cached response for query: '{search_query}'")
            cached_answer = cached_result["answer"]
            sources = cached_result.get("sources", [])

            # Save completed turn to chat history (user_id and session_id are for history)
            if session_id:
                add_guest_chat_turn(session_id, query_text, cached_answer)

            return {
                "query": query_text,
                "search_query": search_query,
                "answer": cached_answer,
                "session_id": session_id,
                "sources": sources,
                "cached": True
            }

        # 5. Cache Miss: Check Vector DB
        print(f"[CACHE MISS] Querying vector DB for '{search_query}'")
        router_service = RouterService()
        doc_id = router_service.route_query_to_document(search_query, db)
        print(f"Routing query '{search_query}' to document ID: {doc_id}")

        query = db.query(DocumentVector)
        if doc_id:
            query = query.filter(DocumentVector.doc_metadata["document_id"].as_integer() == doc_id)

        relevant_chunks = (
            query.order_by(DocumentVector.embedding.cosine_distance(query_vector))
            .limit(top_k)
            .all()
        )

        context_str = "\n\n---\n\n".join([f"[Title: {c.title}]\n{c.content}" for c in relevant_chunks])

        # 6. Final Prompt: Include BOTH Conversation History and Document Context!
        prompt = f"""
        You are a helpful assistant. Use the conversation history and document context to answer the question.

        Conversation History:
        {chat_history_str}

        Document Context:
        {context_str}

        Question: {query_text}
        Answer:
        """

        response = llm.invoke(prompt)
        final_answer = str(response.content).strip()

        sources = [{"title": c.title, "metadata": c.doc_metadata} for c in relevant_chunks]

        # 7. Store new response into semantic cache for future queries
        try:
            semantic_cache.store(
                prompt=search_query,
                response=final_answer,
                sources=sources,
                query_vector=query_vector,
                user_type=user_type,
                user_id=user_id,
                session_id=session_id
            )
        except Exception as e:
            print(f"[SemanticCache Store Exception]: {e}")

        # 8. Save completed turn to chat history (user_id and session_id are for history)
        if session_id:
            add_guest_chat_turn(session_id, query_text, final_answer)

        return {
            "query": query_text,
            "search_query": search_query,
            "answer": final_answer,
            "session_id": session_id,
            "sources": sources,
            "cached": False
        }
    finally:
        if db:
            db.close()

    
