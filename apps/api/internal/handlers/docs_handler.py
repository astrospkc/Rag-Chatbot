from internal.tasks.rag_tasks import run_ingestion_pipeline
from internal.rag.embeddings import EmbeddingModelConfig
from internal.rag.embeddings import EmbeddingFactory
from internal.rag.embeddings.embeddings import LangChainEmbeddingsAdapter
from internal.rag.embeddings.embeddings import LangChainEmbeddings
from internal.rag.chunking.chunking import LangChainChunkerAdapter
from internal.rag.chunking.chunking import RecursiveChunker
from internal.rag.loaders.documentLoader import DocumentLoader
from fastapi import APIRouter, UploadFile, BackgroundTasks
import os
# from internal.rag.pipeline import ingestion_pipeline

router = APIRouter()


@router.post("/documents")
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks
):

    file_path = f"/tmp/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # background_tasks.add_task(
    #     ingestion_pipeline.run,
    #     file_path
    # )

    return {
        "message": "Document accepted",
        "status": "processing"
    }

@router.post("/doc")
async def upload_doc(background_tasks: BackgroundTasks):
    filepath = "/home/punam/Documents/punam_2/punam/punam/ai_projects/new_ai_projects/rag_chatbot/apps/api/telepsychics-pdfdrive-.pdf"
    run_ingestion_pipeline.delay(filepath)
    return {
        "message": "Document accepted",
        "status": "processing"
    }

# @router.post("/doc")
# async def upload_doc(background_tasks: BackgroundTasks):
    # Hardcoded relative or absolute path to the local PDF file inside apps/api
    # aws set up for file upload 
    
    filepath = "/home/punam/Documents/punam_2/punam/punam/ai_projects/new_ai_projects/rag_chatbot/apps/api/telepsychics-pdfdrive-.pdf"

    # this will be done later-----
    # # Trigger background ingestion task for testing
    # background_tasks.add_task(
    #     ingestion_pipeline.run,
    #     filepath
    # )

    # 1. pdf will be loaded
    # 2. chunking 
    # 3. embedding generation
    # 4. embedding + text will be saved in postgres db
    # 5. vector store
    # 6. FAISS index will be created 

    # pdf loader
    document_loader = DocumentLoader(filepath)
    document = document_loader.load()

    # print("pdf document load: ", document)
    
    recursive_chunker = RecursiveChunker(chunk_size=1000, chunk_overlap=200)
    chunked_documents = recursive_chunker.chunk(document)
    # chunked_documents = recursive_chunker.chunk_list(document, chunk_size=100)

    
    # extract page contents
    texts = [doc.page_content for doc in chunked_documents]
    print("texts: ",len(texts))
    # print("text: ", texts[0])

    config = EmbeddingModelConfig(
        model_name="nvidia/nemotron-3-embed-1b:free",
        dimensions=768
    )
    # provider from embedding factory
    embed_provider = EmbeddingFactory.get_provider("openai",model_name=config.model_name,api_key=os.getenv("OPENROUTER_ADMIN_KEY"))

    # generate embedding for all text chunks
    embeddings = embed_provider.embed_documents_with_rate_limit(texts)
    
    print("embeddings length: ", len(embeddings))
    print("embedding:", embeddings[0])
    # now insert in the vector store


    
    

    return {
        "message": "Test document queued for processing",
        "file": filepath,
        "status": "processing"
    }