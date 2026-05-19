# Python NLP Service — Risk Scoring

## 職責

根據情緒軌跡特徵，對每位用戶輸出風險等級，推送給 Spring Boot Service。

## 風險等級定義

| 等級 | 說明 | 臨床意義 |
|---|---|---|
| `HIGH` | 需要立即關注 | 觸發 Alert，通知醫護人員 |
| `MEDIUM` | 需要持續觀察 | 記錄追蹤，不立即通知 |
| `LOW` | 情緒相對穩定 | 正常記錄 |
| `INSUFFICIENT_DATA` | 資料不足 | 不評分，不推送 |

## 評分規則

規則採用**優先順序判斷**，第一條符合即停止：

```python
from enum import Enum

class RiskLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

def score_risk(trajectory: UserTrajectory | None) -> RiskLevel:
    if trajectory is None or trajectory.data_points < 3:
        return RiskLevel.INSUFFICIENT_DATA

    # HIGH：任一條件成立
    if (
        trajectory.consecutive_negative_days >= 7
        or trajectory.score_drop_pct >= 40.0
        or (trajectory.rolling_avg_7d >= 0.80 and trajectory.slope_7d > 0.05)
    ):
        return RiskLevel.HIGH

    # MEDIUM：任一條件成立
    if (
        trajectory.consecutive_negative_days >= 3
        or trajectory.score_drop_pct >= 20.0
        or trajectory.rolling_avg_7d >= 0.65
        or trajectory.post_frequency_change <= -0.50  # 發文量減少50%以上
    ):
        return RiskLevel.MEDIUM

    return RiskLevel.LOW
```

## 規則說明

| 規則 | 臨床依據 |
|---|---|
| 連續 7 天負面 | 持續情緒低落超過一週是臨床憂鬱症診斷標準之一 |
| 情緒分數急降 40% | 相對基準的顯著惡化，非正常波動 |
| 7 天均值 ≥ 0.80 且上升中 | 高負面情緒且持續惡化 |
| 發文量減少 50% | 社交退縮是憂鬱症早期行為指標 |

## 推送格式

```python
@dataclass
class EmotionRecordPayload:
    external_user_id: str
    source: str                  # "reddit" | "mimic"
    post_id: str
    text_snippet: str            # 前 200 字
    posted_at: datetime
    emotion_label: str
    emotion_score: float
    risk_level: str              # RiskLevel value

def build_batch_payload(
    records: list[EmotionResult],
    risk_map: dict[str, RiskLevel],
) -> dict:
    return {
        "source": records[0].source if records else "unknown",
        "records": [
            {
                "external_user_id": r.external_user_id,
                "post_id": r.record_id,
                "text_snippet": r.text_snippet,
                "posted_at": r.recorded_at.isoformat(),
                "emotion_label": r.emotion_label,
                "emotion_score": r.emotion_score,
                "risk_level": risk_map.get(r.external_user_id, RiskLevel.LOW).value,
            }
            for r in records
        ],
    }
```

## 規則調整機制

風險規則閾值存在環境變數，不硬編碼在程式中：

```env
RISK_HIGH_CONSECUTIVE_DAYS=7
RISK_HIGH_DROP_PCT=40.0
RISK_HIGH_AVG_THRESHOLD=0.80
RISK_MEDIUM_CONSECUTIVE_DAYS=3
RISK_MEDIUM_DROP_PCT=20.0
RISK_MEDIUM_AVG_THRESHOLD=0.65
RISK_MEDIUM_FREQ_DROP=0.50
```

Phase 2 收集更多資料後，可根據實際分布調整閾值，不需改程式。

## 相關 Spec

- [Trajectory Modeling](2026-05-19-trajectory-modeling.md)
- [Spring Boot Service Overview](../spring-boot-service/2026-05-19-service-overview.md)
- [Intervention Engine](../spring-boot-service/2026-05-19-intervention-engine.md)
