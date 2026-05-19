import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

import scheduler as sched
from nlp.emotion_classifier import _get_classifier
from scheduler import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

app_state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up model on startup
    _get_classifier()
    sched.start(app_state)
    yield
    if "scheduler" in app_state:
        app_state["scheduler"].shutdown()


app = FastAPI(
    title="OncoPulse — NLP Service",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/status")
def status():
    scheduler = app_state.get("scheduler")
    jobs = []
    if scheduler:
        for job in scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "next_run": str(job.next_run_time),
            })
    return {"scheduler_running": scheduler is not None, "jobs": jobs}


@app.post("/api/v1/analyze/run-now")
def run_now():
    """Manually trigger the pipeline (for development / testing)."""
    run_pipeline()
    return {"status": "pipeline triggered"}
