from fastapi import APIRouter, UploadFile, BackgroundTasks
from internal.rag.pipeline import ingestion_pipeline

router = APIRouter()


@router.post("/documents")
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks
):

    file_path = f"/tmp/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    background_tasks.add_task(
        ingestion_pipeline.run,
        file_path
    )

    return {
        "message": "Document accepted",
        "status": "processing"
    }