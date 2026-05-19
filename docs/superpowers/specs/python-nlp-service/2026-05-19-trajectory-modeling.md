# Python NLP Service — Trajectory Modeling

## 職責

將同一用戶在不同時間點的情緒分數串成時間序列，計算情緒軌跡特徵，供風險評分使用。

## 核心概念

單一情緒分類結果意義有限，情緒**隨時間的變化趨勢**才是預測風險的關鍵。本模組將個別情緒紀錄聚合為用戶層級的軌跡，計算以下特徵：

| 特徵 | 說明 |
|---|---|
| `rolling_avg_7d` | 過去 7 天負面情緒分數移動平均 |
| `rolling_avg_3d` | 過去 3 天負面情緒分數移動平均 |
| `slope_7d` | 7 天情緒趨勢斜率（負值代表惡化中）|
| `consecutive_negative_days` | 連續負面情緒天數 |
| `score_drop_pct` | 與 30 天前基準值的下降百分比 |
| `post_frequency_change` | 發文頻率變化（減少可能代表社交退縮）|

## 計算邏輯

```python
import pandas as pd
import numpy as np
from dataclasses import dataclass

@dataclass
class UserTrajectory:
    external_user_id: str
    calculated_at: datetime
    rolling_avg_7d: float
    rolling_avg_3d: float
    slope_7d: float
    consecutive_negative_days: int
    score_drop_pct: float
    post_frequency_change: float
    data_points: int             # 用於計算的資料點數量

def compute_trajectory(
    user_id: str,
    emotion_records: list[EmotionResult],
) -> UserTrajectory | None:

    if len(emotion_records) < 3:
        return None  # 資料不足，無法建立軌跡

    df = pd.DataFrame([{
        "date": r.recorded_at.date(),
        "negative_score": r.negative_score,
        "is_negative": r.emotion_label == "negative",
    } for r in emotion_records])

    # 按日期聚合（取每天平均）
    daily = df.groupby("date").agg(
        negative_score=("negative_score", "mean"),
        is_negative=("is_negative", "any"),
    ).reset_index().sort_values("date")

    # 移動平均
    daily["roll_7d"] = daily["negative_score"].rolling(7, min_periods=1).mean()
    daily["roll_3d"] = daily["negative_score"].rolling(3, min_periods=1).mean()

    # 7 天斜率（線性回歸）
    last_7 = daily.tail(7)
    if len(last_7) >= 2:
        x = np.arange(len(last_7))
        slope = float(np.polyfit(x, last_7["negative_score"].values, 1)[0])
    else:
        slope = 0.0

    # 連續負面天數
    consecutive = 0
    for is_neg in reversed(daily["is_negative"].values):
        if is_neg:
            consecutive += 1
        else:
            break

    # 與 30 天前基準比較
    baseline = daily.head(min(7, len(daily)))["negative_score"].mean()
    recent = daily.tail(7)["negative_score"].mean()
    drop_pct = ((recent - baseline) / baseline * 100) if baseline > 0 else 0.0

    # 發文頻率變化（前半段 vs 後半段天數）
    mid = len(daily) // 2
    freq_before = len(daily[:mid])
    freq_after = len(daily[mid:])
    freq_change = (freq_after - freq_before) / max(freq_before, 1)

    return UserTrajectory(
        external_user_id=user_id,
        calculated_at=datetime.now(timezone.utc),
        rolling_avg_7d=float(daily["roll_7d"].iloc[-1]),
        rolling_avg_3d=float(daily["roll_3d"].iloc[-1]),
        slope_7d=slope,
        consecutive_negative_days=consecutive,
        score_drop_pct=drop_pct,
        post_frequency_change=freq_change,
        data_points=len(daily),
    )
```

## 最少資料需求

| 條件 | 最低需求 |
|---|---|
| 計算任何軌跡特徵 | 至少 3 天的紀錄 |
| 7 天移動平均有意義 | 至少 7 天 |
| 斜率可信 | 至少 5 天 |

資料不足的用戶回傳 `None`，不進入風險評分，不推送給 Spring Boot。

## 更新頻率

- 每小時排程執行後，對本次有新貼文的用戶重新計算軌跡
- 歷史軌跡不重算（節省運算資源）

## 相關 Spec

- [Emotion Classification](2026-05-19-emotion-classification.md)
- [Risk Scoring](2026-05-19-risk-scoring.md)
