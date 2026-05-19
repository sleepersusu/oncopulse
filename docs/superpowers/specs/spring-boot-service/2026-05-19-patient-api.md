# Spring Boot Service — Patient API

## 職責

管理系統中追蹤的用戶（來自 Reddit 或 MIMIC-III），提供查詢與維護端點給前端。

## Endpoints

### `GET /api/v1/patients`

取得病患清單，支援過濾與分頁。

**Query Parameters**

| 參數 | 類型 | 說明 |
|---|---|---|
| `riskLevel` | string | 過濾風險等級：`HIGH` / `MEDIUM` / `LOW` |
| `source` | string | 過濾來源：`reddit` / `mimic` / `pilot` |
| `isActive` | boolean | 是否只看活躍用戶，預設 `true` |
| `page` | int | 頁碼，預設 0 |
| `size` | int | 每頁筆數，預設 20，最大 100 |
| `sort` | string | 排序欄位，預設 `lastSeenAt,desc` |

**Response 200**

```json
{
  "content": [
    {
      "id": "uuid",
      "externalUserId": "sha256_hash",
      "source": "reddit",
      "firstSeenAt": "2026-04-01T00:00:00Z",
      "lastSeenAt": "2026-05-19T10:00:00Z",
      "currentRiskLevel": "HIGH",
      "totalRecords": 42,
      "isActive": true
    }
  ],
  "totalElements": 150,
  "totalPages": 8,
  "page": 0,
  "size": 20
}
```

---

### `GET /api/v1/patients/{id}`

取得單一病患詳情。

**Response 200**

```json
{
  "id": "uuid",
  "externalUserId": "sha256_hash",
  "source": "reddit",
  "firstSeenAt": "2026-04-01T00:00:00Z",
  "lastSeenAt": "2026-05-19T10:00:00Z",
  "currentRiskLevel": "HIGH",
  "totalRecords": 42,
  "recentEmotionSummary": {
    "rollingAvg7d": 0.82,
    "consecutiveNegativeDays": 9,
    "scoreDropPct": 45.2
  },
  "openAlertsCount": 2,
  "isActive": true
}
```

**Response 404**

```json
{ "error": "Patient not found", "id": "uuid" }
```

---

### `POST /api/v1/patients`

手動新增病患（供 Pilot Study 使用，病患填完同意書後由管理員建立）。

**Request Body**

```json
{
  "externalUserId": "pilot_participant_001",
  "source": "pilot"
}
```

**Response 201**

```json
{
  "id": "uuid",
  "externalUserId": "pilot_participant_001",
  "source": "pilot",
  "currentRiskLevel": "LOW",
  "createdAt": "2026-05-19T10:00:00Z"
}
```

**Response 409** （external_user_id 重複）

```json
{ "error": "Patient with this externalUserId already exists" }
```

---

### `PUT /api/v1/patients/{id}`

更新病患狀態（目前只支援 `isActive`）。

**Request Body**

```json
{
  "isActive": false
}
```

**Response 200** 回傳更新後的完整病患資料。

---

### `DELETE /api/v1/patients/{id}`

軟刪除：將 `isActive` 設為 false，保留歷史紀錄。
不做實際 DELETE，符合資料可稽核原則。

**Response 204** No Content

## 業務邏輯

- `currentRiskLevel` 由 Python Service 推送後由 `InterventionEngine` 更新，不由 Patient API 直接寫入
- `totalRecords` 從 `emotion_records` count 計算，不冗餘儲存
- `firstSeenAt` / `lastSeenAt` 在每次收到新 emotion record 時自動更新

## 相關 Spec

- [Database Schema](2026-05-19-database-schema.md)
- [Emotion Record API](2026-05-19-emotion-record-api.md)
