#!/usr/bin/env python3
"""
Celery Worker Configuration

Sets up Celery with Redis broker for task queue management
"""

import os
import logging
from dotenv import load_dotenv
from celery import Celery

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Broker and backend configuration
broker_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
result_backend = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app instance
app = Celery(
    "opus_tasks",
    broker=broker_url,
    backend=result_backend,
    include=["src.worker.tasks"]
)

# Configure Celery
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_concurrency=4,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_max_tasks_per_child=10,
    broker_connection_retry_on_startup=True
)

# Task routing
app.conf.task_routes = {
    "src.worker.tasks.process_video_task": {"queue": "processing"},
    "src.worker.tasks.render_video_task": {"queue": "rendering"},
    "src.worker.tasks.upload_video_task": {"queue": "uploading"},
    "src.worker.tasks.scrape_analytics_task": {"queue": "scraping"}
}

logger.info(f"Celery app initialized with broker: {broker_url}")
logger.info(f"Task queues configured: processing, rendering, uploading, scraping")
