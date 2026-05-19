# Master Architecture — Cancer Patient Emotion Monitoring System

## 研究問題

癌症病患在確診後的文字表達，能否用來早期偵測情緒惡化，並在高風險時點觸發臨床介入提示？

依據 Julian Hong et al. (*Cancer*, 2026) 研究：10.6% 癌症病患在確診後一年內出現新的心理健康疾患，且全因死亡率顯著升高（HR 1.51）。目前臨床端缺乏主動偵測機制，本系統目標是在情緒崩潰前偵測到訊號。

## 系統目標

- 從公開文字資料訓練並驗證情緒偵測模型
- 追蹤個別病患的情緒時間序列軌跡，非單一時間點快照
- 高風險時觸發 Alert 通知醫護人員
- 提供臨床 Dashboard 供醫護查看病患情緒狀態

## 三服務架構

```
┌─────────────────────────────────────────────────────────┐
│              Python NLP Service（Port 8001）              │
│  資料收集 → 情緒分類 → 軌跡建模 → 風險分級 → REST API    │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (JSON)
                         │ POST /api/v1/emotion-records/batch
                         ▼
┌─────────────────────────────────────────────────────────┐
│           Spring Boot Service（Port 8080）               │
│  病患管理、情緒紀錄儲存、介入規則引擎、Alert 管理         │
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
      ┌────────▼────────┐    ┌────────▼──────────────────┐
      │   PostgreSQL     │    │   React / Vue Frontend     │
      │   Port 5432      │    │   Port 3000                │
      │                  │    │   情緒軌跡圖、高風險列表   │
      └──────────────────┘    └───────────────────────────┘
```

## 服務職責分工

| 服務 | 語言/框架 | 職責 |
|---|---|---|
| Python NLP Service | Python 3.11 + FastAPI | 資料收集、NLP 分析、風險評分、定期推送結果 |
| Spring Boot Service | Java 21 + Spring Boot 3 | 資料持久化、業務邏輯、API Gateway、規則引擎 |
| Frontend Service | React 18 + TypeScript | 視覺化 Dashboard、Alert 操作介面 |
| Database | PostgreSQL 16 | 所有持久化資料 |

## 資料流

```
1. Python Service 每小時從 Reddit API 抓取新貼文
2. 對每則貼文做情緒分類（HuggingFace 模型）
3. 計算用戶情緒軌跡 + 風險分級
4. 推送結果到 Spring Boot POST /api/v1/emotion-records/batch
5. Spring Boot 規則引擎判斷是否觸發 Alert
6. 若觸發，建立 Alert 記錄到 PostgreSQL
7. 前端從 Spring Boot 拉取資料，顯示 Dashboard
```

## 資料來源策略

| 階段 | 資料來源 | 用途 |
|---|---|---|
| Phase 1 | Reddit r/cancer（公開 API）| 模型訓練與驗證 |
| Phase 2 | MIMIC-III（PhysioNet 申請）| 臨床筆記驗證 |
| Phase 3 | 同意書病患自述文字 | Pilot 介入研究 |

Phase 1–2 資料皆為匿名，不涉及個人識別。Phase 3 需 IRB 審查。

## 倫理設計原則

- 公開資料只用於訓練，不做個人介入
- 臨床介入僅對有 informed consent 的病患
- HIGH RISK Alert 通知醫護人員，系統不直接對病患發訊
- 病患資料加密存儲，PostgreSQL 欄位敏感資料使用 AES-256
- 符合 HIPAA 基本原則

## 服務間 API 契約

### Python → Spring Boot

```
POST /api/v1/emotion-records/batch
Content-Type: application/json

{
  "source": "reddit",
  "records": [
    {
      "external_user_id": "reddit_user_hash_abc123",
      "post_id": "t3_xyz",
      "post_text": "...",
      "posted_at": "2026-05-19T10:00:00Z",
      "emotion_label": "negative",
      "emotion_score": 0.87,
      "risk_level": "HIGH"
    }
  ]
}
```

### Spring Boot → Frontend

所有 Frontend 資料來源均為 Spring Boot REST API，詳見各 API spec。

## 相關 Spec 文件

- [Python NLP Service Overview](python-nlp-service/2026-05-19-service-overview.md)
- [Spring Boot Service Overview](spring-boot-service/2026-05-19-service-overview.md)
- [Frontend Service Overview](frontend-service/2026-05-19-service-overview.md)
- [Database Schema](spring-boot-service/2026-05-19-database-schema.md)

## 對接 Berkeley CPH 教授

| 教授 | 機構 | 本系統的關聯 |
|---|---|---|
| Julian Hong, MD | UCSF 放射腫瘤科 | 直接延伸其癌症×心理健康研究缺口 |
| Irene Chen, PhD | Berkeley CPH | 臨床 AI 公平性、LLM 在醫療的評估 |
| Adrian Aguilera, PhD | Berkeley dHEAL | 數位心理健康介入設計框架 |
