# Spring Boot Service — Database Schema

## 資料庫：PostgreSQL 16

所有 schema 變更透過 Flyway 管理，不直接改資料庫。

## ERD（實體關係）

```
patients ──────────────── emotion_records
    │                          │
    │                          │ (external_user_id 對應，非 FK)
    │
    └──────────────────── alerts
                               │
                          (由 intervention_engine 產生)
```

## 資料表定義

### `patients`

```sql
CREATE TABLE patients (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_user_id    VARCHAR(64) NOT NULL UNIQUE,  -- hash 後的用戶 ID
    source              VARCHAR(20) NOT NULL,          -- 'reddit' | 'mimic' | 'pilot'
    first_seen_at       TIMESTAMP WITH TIME ZONE NOT NULL,
    last_seen_at        TIMESTAMP WITH TIME ZONE NOT NULL,
    current_risk_level  VARCHAR(20) NOT NULL DEFAULT 'LOW',
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_patients_external_user_id ON patients(external_user_id);
CREATE INDEX idx_patients_risk_level ON patients(current_risk_level);
```

**注意：** `patients` 表不儲存任何可識別個人的資訊（姓名、帳號等），只有 hash 後的 ID。

---

### `emotion_records`

```sql
CREATE TABLE emotion_records (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id          UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    source              VARCHAR(20) NOT NULL,
    post_id             VARCHAR(64) NOT NULL,
    text_snippet        TEXT,                          -- 前 200 字，非全文
    posted_at           TIMESTAMP WITH TIME ZONE NOT NULL,
    emotion_label       VARCHAR(20) NOT NULL,          -- 'positive' | 'neutral' | 'negative'
    emotion_score       DECIMAL(5,4) NOT NULL,
    positive_score      DECIMAL(5,4),
    neutral_score       DECIMAL(5,4),
    negative_score      DECIMAL(5,4),
    risk_level          VARCHAR(20) NOT NULL,
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_post UNIQUE (source, post_id)
);

CREATE INDEX idx_emotion_records_patient_id ON emotion_records(patient_id);
CREATE INDEX idx_emotion_records_posted_at ON emotion_records(posted_at DESC);
CREATE INDEX idx_emotion_records_risk_level ON emotion_records(risk_level);
```

---

### `alerts`

```sql
CREATE TABLE alerts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id          UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    risk_level          VARCHAR(20) NOT NULL,
    trigger_reason      TEXT NOT NULL,                 -- 觸發原因描述（給醫護看）
    status              VARCHAR(20) NOT NULL DEFAULT 'OPEN',
                                                       -- 'OPEN' | 'ACKNOWLEDGED' | 'RESOLVED'
    acknowledged_by     VARCHAR(100),                  -- 醫護人員名稱或 ID
    acknowledged_at     TIMESTAMP WITH TIME ZONE,
    resolved_at         TIMESTAMP WITH TIME ZONE,
    notes               TEXT,                          -- 醫護備註
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_alerts_patient_id ON alerts(patient_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);
```

---

### `users`（醫護人員帳號，非病患）

```sql
CREATE TABLE users (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username            VARCHAR(100) NOT NULL UNIQUE,
    password_hash       VARCHAR(255) NOT NULL,         -- bcrypt
    display_name        VARCHAR(100) NOT NULL,
    role                VARCHAR(20) NOT NULL DEFAULT 'CLINICIAN',
                                                       -- 'ADMIN' | 'CLINICIAN'
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

## Flyway Migration 命名規範

```
V1__create_patients_table.sql
V2__create_emotion_records_table.sql
V3__create_alerts_table.sql
V4__create_users_table.sql
```

## 敏感資料處理

- `text_snippet` 只存前 200 字，不存原始完整貼文
- `external_user_id` 全程為 hash，不存原始用戶名
- 資料庫 connection 使用 SSL（`sslmode=require`）
- 備份加密

## 相關 Spec

- [Service Overview](2026-05-19-service-overview.md)
- [Patient API](2026-05-19-patient-api.md)
- [Emotion Record API](2026-05-19-emotion-record-api.md)
- [Alert API](2026-05-19-alert-api.md)
