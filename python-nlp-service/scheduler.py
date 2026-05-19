import logging
from collections import defaultdict

from apscheduler.schedulers.background import BackgroundScheduler

from collectors import reddit_collector
from config import settings
from models.schemas import EmotionResult
from nlp import emotion_classifier, risk_scorer, trajectory_modeler
from pusher import spring_boot_pusher

logger = logging.getLogger(__name__)

# In-memory accumulation across pipeline runs.
# key: external_user_id, value: list of all EmotionResult seen so far.
# Resets on process restart (acceptable for Phase 1).
_history: dict[str, list[EmotionResult]] = defaultdict(list)

# Prevent unbounded growth: keep at most this many records per user.
_MAX_RECORDS_PER_USER = 500


def _accumulate(new_results: list[EmotionResult]) -> None:
    for r in new_results:
        bucket = _history[r.external_user_id]
        bucket.append(r)
        if len(bucket) > _MAX_RECORDS_PER_USER:
            # Drop oldest to stay within limit
            _history[r.external_user_id] = bucket[-_MAX_RECORDS_PER_USER:]


def run_pipeline() -> None:
    logger.info("Pipeline started")

    # 1. Collect
    records = reddit_collector.collect_all()
    logger.info("Collected %d records total", len(records))
    if not records:
        return

    # 2. Classify
    new_results = emotion_classifier.classify_batch(records)
    logger.info("Classified %d records", len(new_results))

    # 3. Accumulate into history so trajectory has enough data across runs
    _accumulate(new_results)

    # 4. Compute trajectory from full accumulated history
    all_known_results = [r for bucket in _history.values() for r in bucket]
    trajectories = trajectory_modeler.compute_all(all_known_results)
    logger.info(
        "Trajectories computed: %d users with enough data (out of %d tracked)",
        len(trajectories),
        len(_history),
    )

    # 5. Risk score
    risk_map = {uid: risk_scorer.score(t) for uid, t in trajectories.items()}

    # 6. Push only the NEW records from this run (not full history)
    spring_boot_pusher.push("reddit", new_results, risk_map)

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
