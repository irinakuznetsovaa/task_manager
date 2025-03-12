from celery import Celery
from app.core.config import settings
celery_app = Celery(
    "task_manager",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
    include=["app.infrastructure.workers.tasks"],
)


celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
