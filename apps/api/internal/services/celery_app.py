import os
from celery import Celery
from kombu import Queue
from dotenv import load_dotenv

load_dotenv()

broker_url = os.getenv("RABBITMQ_URL") or os.getenv("CLOUDAMQP_URL") or "amqp://guest:guest@localhost:5672//"

celery_app = Celery(
    "rag_app",
    
    broker=broker_url,
    include=["internal.tasks.rag_tasks"]
)

# celery_app.conf.task_queues = (
#     Queue("rag"),
# )

# celery_app.conf.task_default_queue = "rag"

# celery_app.conf.worker_prefetch_multiplier = 1