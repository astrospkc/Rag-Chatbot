from internal.services.celery_app import celery_app
from kombu import Queue

celery_app.conf.task_queues = (
    Queue("rag"),
)

celery_app.conf.task_default_queue = "rag"

celery_app.conf.worker_prefetch_multiplier = 1


@celery_app.task(queue="rag")
def run_ingestion_pipeline(file_path: str):
    print("Processing file:", file_path)
    # Here you will call your existing ingestion pipeline
    # For now, let's just simulate it
    return f"Processed {file_path}"