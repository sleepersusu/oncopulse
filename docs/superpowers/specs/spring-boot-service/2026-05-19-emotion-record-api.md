# Spring Boot Service — Emotion Record API

## 職責

接收 Python NLP Service 推送的情緒分析結果（批次），並提供前端查詢病患情緒紀錄與軌跡的端點。

## Endpoints

### `POST /api/v1/emotion-records/batch`

Python NLP Service 專用端點，定時推送批次情緒分析結果。

**認證：** Header `X-API-Key: {NLP_SERVICE_API_KEY}`

**Request Body**

```json
{
  "source": "reddit",
  "records": [
    {
      "externalUserId": "sha256_hash_abc",
      "postId": "t3_xyz123",
      "textSnippet": "Just got my diagnosis today. I don't know how to...",
      "postedAt": "2026-05-19T08:30:00Z",
      "emotionLabel": "negative",
      "emotionScore": 0.9123,
      "positiveScore": 0.0210,
      "neutralScore": 0.0667,
      "negativeScore": 0.9123,
      "riskLevel": "HIGH"
    }
  ]
}
```

**處理邏輯**

```
1. 驗證 API Key
2. 逐筆處理 records：
   a. 依 externalUserId 查找或建立 Patient
   b. 若 postId 已存在（UNIQUE constraint），跳過（idempotent）
   c. 儲存 EmotionRecord
   d. 更新 Patient.lastSeenAt、Patient.currentRiskLevel
3. 批次完成後，對有 HIGH risk 的 Patient 觸發 InterventionEngine
4. 回傳處理摘要
```

**Response 200**

```json
{
  "received": 50,
  "saved": 48,
  "skipped": 2,
  "alertsTriggered": 3,
  "processedAt": "2026-05-19T10:05:00Z"
}
```

**Response 400** 格式錯誤

**Response 401** API Key 無效

---

### `GET /api/v1/patients/{id}/emotion-records`

取得指定病患的情緒紀錄清單。

**Query Parameters**

| 參數 | 類型 | 說明 |
|---|---|---|
| `from` | ISO date | 開始日期，預設 30 天前 |
| `to` | ISO date | 結束日期，預設今天 |
| `emotionLabel` | string | 過濾情緒標籤 |
| `page` | int | 頁碼，預設 0 |
| `size` | int | 每頁筆數，預設 50 |

**Response 200**

```json
{
  "content": [
    {
      "id": "uuid",
      "patientId": "uuid",
      "source": "reddit",
      "postId": "t3_xyz123",
      "textSnippet": "Just got my diagnosis today...",
      "postedAt": "2026-05-19T08:30:00Z",
      "emotionLabel": "negative",
      "emotionScore": 0.9123,
      "riskLevel": "HIGH"
    }
  ],
  "totalElements": 42,
  "page": 0,
  "size": 50
}
```

---

### `GET /api/v1/patients/{id}/emotion-trajectory`

取得病患情緒軌跡，供前端折線圖使用。

**Query Parameters**

| 參數 | 類型 | 說明 |
|---|---|---|
| `days` | int | 查詢天數，預設 30，最大 90 |
| `granularity` | string | `daily`（預設）/ `weekly` |

**Response 200**

```json
{
  "patientId": "uuid",
  "from": "2026-04-19",
  "to": "2026-05-19",
  "granularity": "daily",
  "dataPoints": [
    {
      "date": "2026-04-19",
      "avgNegativeScore": 0.42,
      "avgPositiveScore": 0.35,
      "recordCount": 3,
      "dominantEmotion": "neutral"
    },
    {
      "date": "2026-04-20",
      "avgNegativeScore": 0.71,
      "avgPositiveScore": 0.12,
      "recordCount": 5,
      "dominantEmotion": "negative"
    }
  ],
  "summary": {
    "rollingAvg7d": 0.82,
    "slope7d": 0.08,
    "consecutiveNegativeDays": 9,
    "scoreDropPct": 45.2,
    "currentRiskLevel": "HIGH"
  }
}
```

## 相關 Spec

- [Database Schema](2026-05-19-database-schema.md)
- [Intervention Engine](2026-05-19-intervention-engine.md)
- [Frontend Trajectory Chart](../frontend-service/2026-05-19-trajectory-chart.md)
