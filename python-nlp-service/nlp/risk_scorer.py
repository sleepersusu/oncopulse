from config import settings
from models.schemas import RiskLevel, UserTrajectory


def score(trajectory: UserTrajectory | None) -> RiskLevel:
    if trajectory is None or trajectory.data_points < 3:
        return RiskLevel.INSUFFICIENT_DATA

    s = settings

    if (
        trajectory.consecutive_negative_days >= s.risk_high_consecutive_days
        or trajectory.score_drop_pct >= s.risk_high_drop_pct
        or (
            trajectory.rolling_avg_7d >= s.risk_high_avg_threshold
            and trajectory.slope_7d > 0.05
        )
    ):
        return RiskLevel.HIGH

    if (
        trajectory.consecutive_negative_days >= s.risk_medium_consecutive_days
        or trajectory.score_drop_pct >= s.risk_medium_drop_pct
        or trajectory.rolling_avg_7d >= s.risk_medium_avg_threshold
        or trajectory.post_frequency_change <= -s.risk_medium_freq_drop
    ):
        return RiskLevel.MEDIUM

    return RiskLevel.LOW
