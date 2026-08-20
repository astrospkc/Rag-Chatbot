from internal.rag.loaders.documentLoader import DocumentLoader
from fastapi import APIRouter, UploadFile, BackgroundTasks
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
    # Hardcoded relative or absolute path to the local PDF file inside apps/api
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

    print("pdf document load: ", document)

    return {
        "message": "Test document queued for processing",
        "file": filepath,
        "status": "processing"
    }