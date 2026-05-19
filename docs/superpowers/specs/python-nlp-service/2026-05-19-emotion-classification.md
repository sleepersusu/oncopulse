# Python NLP Service — Emotion Classification

## 職責

對每則文字記錄進行情緒分類，輸出情緒標籤與信心分數。

## 模型選擇

### 主要模型

```
cardiffnlp/twitter-roberta-base-sentiment-latest
```

- 基於 RoBERTa，在 Twitter 資料上微調
- 輸出三類：`positive` / `neutral` / `negative`
- 在非正式社群文字（論壇、社群媒體）上表現穩定
- HuggingFace 免費使用，不需 API key

### 備用模型（心理健康專用）

```
mental/mental-roberta-base
```

- 專門針對心理健康相關文字訓練
- 若 Phase 2 評估後主要模型表現不足，切換至此

### 模型比較（啟動時決定）

| 模型 | 強項 | 弱項 |
|---|---|---|
| twitter-roberta | 通用社群文字、速度快 | 對醫療術語理解有限 |
| mental-roberta | 心理健康術語理解好 | 訓練資料較小 |

## 分類邏輯

```python
from transformers import pipeline
from dataclasses import dataclass
from datetime import datetime

classifier = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    top_k=None,  # 回傳所有類別分數
)

@dataclass
class EmotionResult:
    external_user_id: str
    source: str
    record_id: str
    recorded_at: datetime
    text_snippet: str        # 前 200 字，不存全文（隱私）
    emotion_label: str       # "positive" | "neutral" | "negative"
    emotion_score: float     # 最高分類別的信心分數 0.0–1.0
    positive_score: float
    neutral_score: float
    negative_score: float

def classify(record: RawTextRecord) -> EmotionResult:
    # 截斷至 512 tokens（模型上限）
    text = record.text[:2000]
    results = classifier(text)[0]

    scores = {r["label"].lower(): r["score"] for r in results}
    dominant = max(scores, key=scores.get)

    return EmotionResult(
        external_user_id=record.external_user_id,
        source=record.source,
        record_id=record.record_id,
        recorded_at=record.recorded_at,
        text_snippet=record.text[:200],
        emotion_label=dominant,
        emotion_score=scores[dominant],
        positive_score=scores.get("positive", 0.0),
        neutral_score=scores.get("neutral", 0.0),
        negative_score=scores.get("negative", 0.0),
    )
```

## 批次處理

```python
def classify_batch(records: list[RawTextRecord], batch_size: int = 32) -> list[EmotionResult]:
    results = []
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        results.extend([classify(r) for r in batch])
    return results
```

## 文字前處理

在送入模型前執行：

```python
import re

def preprocess(text: str) -> str:
    text = re.sub(r"http\S+", "[URL]", text)      # 移除連結
    text = re.sub(r"@\w+", "[USER]", text)         # 匿名化 @ 提及
    text = re.sub(r"\n+", " ", text)               # 換行轉空格
    text = text.strip()
    return text[:2000]                              # 截斷
```

## 評估方法

Phase 1 結束時對分類器做基本評估：

| 評估資料集 | 說明 |
|---|---|
| SemEval-2017 Task 4 | Twitter 情緒分類 benchmark |
| DAIC-WOZ（子集）| 心理健康訪談文字（公開子集）|

指標：Precision、Recall、F1（macro average）

## 效能預期

- 單筆分類：< 100ms（CPU）
- 批次 32 筆：< 1 秒（CPU）
- 每小時 500 則貼文：< 2 分鐘完成

## 相關 Spec

- [Data Collection](2026-05-19-data-collection.md)
- [Trajectory Modeling](2026-05-19-trajectory-modeling.md)
