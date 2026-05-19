# Python NLP Service — Service Overview

## 職責

負責所有 NLP 相關工作：資料收集、情緒分類、時間序列軌跡建模、風險評分。定期將分析結果推送給 Spring Boot Service。

## 技術棧

| 項目 | 選擇 | 原因 |
|---|---|---|
| 語言 | Python 3.11 | NLP 生態系標準 |
| Web Framework | FastAPI | 輕量、async 支援、自動產生 OpenAPI docs |
| NLP | HuggingFace Transformers | 現成情緒分類模型，不需自訓練 |
| 排程 | APScheduler | 定時觸發爬蟲與分析任務 |
| HTTP Client | httpx | async HTTP，推送結果給 Spring Boot |
| 資料處理 | pandas + numpy | 時間序列計算 |
| 容器 | Docker | 與其他服務統一部署 |

## 對外介面

### 提供的 Endpoints（供 Spring Boot 或 Debug 用）

```
GET  /health                    ← 健康檢查
GET  /api/v1/status             ← 目前排程狀態、最後執行時間
POST /api/v1/analyze/text       ← 單筆文字即時分析（Debug 用）
```

### 主動推送（呼叫 Spring Boot）

```
POST {SPRING_BOOT_URL}/api/v1/emotion-records/batch
```
定時執行（預設每小時一次），推送批次分析結果。

## 內部模組結構

```
python-nlp-service/
├── main.py                  ← FastAPI app 進入點
├── config.py                ← 環境變數設定
├── scheduler.py             ← APScheduler 排程設定
│
├── collectors/
│   ├── reddit_collector.py  ← Reddit API 爬蟲
│   └── mimic_collector.py   ← MIMIC-III 資料解析
│
├── nlp/
│   ├── emotion_classifier.py  ← HuggingFace 情緒分類
│   ├── trajectory_modeler.py  ← 時間序列軌跡
│   └── risk_scorer.py         ← 風險分級
│
├── pusher/
│   └── spring_boot_pusher.py  ← 推送結果給 Spring Boot
│
└── models/
    └── schemas.py             ← Pydantic 資料模型
```

## 環境變數

```env
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=

SPRING_BOOT_URL=http://spring-boot-service:8080
PUSH_INTERVAL_MINUTES=60

EMOTION_MODEL_NAME=cardiffnlp/twitter-roberta-base-sentiment-latest
RISK_HIGH_THRESHOLD=0.80
RISK_MEDIUM_THRESHOLD=0.60
```

## 相關 Spec

- [Data Collection](2026-05-19-data-collection.md)
- [Emotion Classification](2026-05-19-emotion-classification.md)
- [Trajectory Modeling](2026-05-19-trajectory-modeling.md)
- [Risk Scoring](2026-05-19-risk-scoring.md)
