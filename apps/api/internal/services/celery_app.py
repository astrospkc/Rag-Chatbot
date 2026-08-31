import os
from celery import Celery
from kombu import Queue
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "rag_app",
    broker=os.getenv("CLOUDAMQP_URL")
)

# celery_app.conf.task_queues = (
#     Queue("rag"),
# )

# celery_app.conf.task_default_queue = "rag"

# celery_app.conf.worker_prefetch_multiplier = 1