import logging

from apscheduler.schedulers.background import BackgroundScheduler

from collectors import reddit_collector
from config import settings
from nlp import emotion_classifier, risk_scorer, trajectory_modeler
from pusher import spring_boot_pusher

logger = logging.getLogger(__name__)


def run_pipeline() -> None:
    logger.info("Pipeline started")

    # 1. Collect
    records = reddit_collector.collect_all()
    logger.info("Collected %d records total", len(records))
    if not records:
        return

    # 2. Classify
    results = emotion_classifier.classify_batch(records)
    logger.info("Classified %d records", len(results))

    # 3. Trajectory
    trajectories = trajectory_modeler.compute_all(results)

    # 4. Risk score
    risk_map = {uid: risk_scorer.score(t) for uid, t in trajectories.items()}

    # 5. Push
    spring_boot_pusher.push("reddit", results, risk_map)

    logger.info("Pipeline finished")


def start(app_state: dict) -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_pipeline,
        trigger="interval",
        minutes=settings.push_interval_minutes,
        id="nlp_pipeline",
        replace_existing=True,
    )
    scheduler.start()
    app_state["scheduler"] = scheduler
    logger.info("Scheduler started — interval=%d min", settings.push_interval_minutes)
    return scheduler
