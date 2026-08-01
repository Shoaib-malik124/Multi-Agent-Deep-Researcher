from celery import Celery
from dotenv import load_dotenv
import os
import ssl

load_dotenv()

celery_app = Celery(
    "research_copilot",
    broker=os.environ["REDIS_URL"],
    backend=os.environ["REDIS_URL"],
    include=["components.orchestrator"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    result_expires=3600,
    broker_use_ssl={
        "ssl_cert_reqs": ssl.CERT_NONE
    },
    redis_backend_use_ssl={
        "ssl_cert_reqs": ssl.CERT_NONE
    },
)