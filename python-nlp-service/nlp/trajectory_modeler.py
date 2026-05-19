import logging
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from models.schemas import EmotionResult, UserTrajectory

logger = logging.getLogger(__name__)


def compute_trajectory(
    user_id: str,
    records: list[EmotionResult],
) -> UserTrajectory | None:
    if len(records) < 3:
        return None

    df = pd.DataFrame([
        {
            "date": r.recorded_at.date(),
            "negative_score": r.negative_score,
            "is_negative": r.emotion_label == "negative",
        }
        for r in records
    ])

    daily = (
        df.groupby("date")
        .agg(negative_score=("negative_score", "mean"), is_negative=("is_negative", "any"))
        .reset_index()
        .sort_values("date")
    )

    daily["roll_7d"] = daily["negative_score"].rolling(7, min_periods=1).mean()
    daily["roll_3d"] = daily["negative_score"].rolling(3, min_periods=1).mean()

    last_7 = daily.tail(7)
    if len(last_7) >= 2:
        x = np.arange(len(last_7))
        slope = float(np.polyfit(x, last_7["negative_score"].values, 1)[0])
    else:
        slope = 0.0

    consecutive = 0
    for is_neg in reversed(daily["is_negative"].tolist()):
        if is_neg:
            consecutive += 1
        else:
            break

    baseline = daily.head(min(7, len(daily)))["negative_score"].mean()
    recent = daily.tail(7)["negative_score"].mean()
    drop_pct = ((recent - baseline) / baseline * 100) if baseline > 0 else 0.0

    mid = len(daily) // 2
    freq_change = (len(daily[mid:]) - len(daily[:mid])) / max(len(daily[:mid]), 1)

    return UserTrajectory(
        external_user_id=user_id,
        calculated_at=datetime.now(tz=timezone.utc),
        rolling_avg_7d=float(daily["roll_7d"].iloc[-1]),
        rolling_avg_3d=float(daily["roll_3d"].iloc[-1]),
        slope_7d=slope,
        consecutive_negative_days=consecutive,
        score_drop_pct=drop_pct,
        post_frequency_change=freq_change,
        data_points=len(daily),
    )


def compute_all(results: list[EmotionResult]) -> dict[str, UserTrajectory]:
    by_user: dict[str, list[EmotionResult]] = {}
    for r in results:
        by_user.setdefault(r.external_user_id, []).append(r)

    trajectories: dict[str, UserTrajectory] = {}
    for user_id, user_records in by_user.items():
        t = compute_trajectory(user_id, user_records)
        if t:
            trajectories[user_id] = t

    logger.info("Trajectories computed for %d/%d users", len(trajectories), len(by_user))
    return trajectories
