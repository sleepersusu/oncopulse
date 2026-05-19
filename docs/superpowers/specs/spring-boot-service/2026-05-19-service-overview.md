# Spring Boot Service — Service Overview

## 職責

系統的核心後端：接收 Python NLP Service 的分析結果、持久化到 PostgreSQL、執行介入規則引擎、管理 Alert、並提供前端所有 REST API。

## 技術棧

| 項目 | 選擇 |
|---|---|
| 語言 | Java 21 |
| Framework | Spring Boot 3.x |
| ORM | Spring Data JPA + Hibernate |
| 資料庫 | PostgreSQL 16 |
| 遷移工具 | Flyway |
| 認證 | Spring Security + JWT |
| API 文件 | springdoc-openapi (Swagger UI) |
| 容器 | Docker |

## 對外 API 總覽

### 供 Python NLP Service 呼叫

```
POST /api/v1/emotion-records/batch    ← 批次接收情緒分析結果
```

### 供 Frontend 呼叫

```
# 病患管理
GET    /api/v1/patients
GET    /api/v1/patients/{id}
POST   /api/v1/patients
PUT    /api/v1/patients/{id}
DELETE /api/v1/patients/{id}

# 情緒紀錄
GET    /api/v1/patients/{id}/emotion-records
GET    /api/v1/patients/{id}/emotion-trajectory

# Alert 管理
GET    /api/v1/alerts
GET    /api/v1/alerts/{id}
PUT    /api/v1/alerts/{id}/acknowledge
PUT    /api/v1/alerts/{id}/resolve

# 儀表板統計
GET    /api/v1/dashboard/summary
GET    /api/v1/dashboard/high-risk-patients
```

### 健康檢查

```
GET    /actuator/health
```

## 內部模組結構

```
spring-boot-service/
├── src/main/java/com/healthcare/
│   ├── config/
│   │   ├── SecurityConfig.java
│   │   └── SwaggerConfig.java
│   │
│   ├── patient/
│   │   ├── Patient.java              (Entity)
│   │   ├── PatientRepository.java
│   │   ├── PatientService.java
│   │   └── PatientController.java
│   │
│   ├── emotion/
│   │   ├── EmotionRecord.java        (Entity)
│   │   ├── EmotionRecordRepository.java
│   │   ├── EmotionRecordService.java
│   │   └── EmotionRecordController.java
│   │
│   ├── alert/
│   │   ├── Alert.java                (Entity)
│   │   ├── AlertRepository.java
│   │   ├── AlertService.java
│   │   └── AlertController.java
│   │
│   ├── engine/
│   │   └── InterventionEngine.java   (規則引擎)
│   │
│   └── dashboard/
│       ├── DashboardService.java
│       └── DashboardController.java
│
└── src/main/resources/
    ├── application.yml
    └── db/migration/                 (Flyway migrations)
```

## 環境變數

```yaml
# application.yml
spring:
  datasource:
    url: ${DB_URL:jdbc:postgresql://localhost:5432/healthcare}
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
  jpa:
    hibernate:
      ddl-auto: validate  # Flyway 管理 schema，不讓 Hibernate 自動改
  flyway:
    enabled: true

app:
  jwt:
    secret: ${JWT_SECRET}
    expiration-ms: 86400000  # 24 小時

  nlp-service:
    api-key: ${NLP_SERVICE_API_KEY}  # Python service 推送時帶此 key 驗證
```

## 認證設計

- 前端用 JWT 登入
- Python Service 用靜態 API Key（Header: `X-API-Key`）驗證推送請求
- 公開端點：`/actuator/health`、`/api/v1/auth/login`

## 相關 Spec

- [Database Schema](2026-05-19-database-schema.md)
- [Patient API](2026-05-19-patient-api.md)
- [Emotion Record API](2026-05-19-emotion-record-api.md)
- [Intervention Engine](2026-05-19-intervention-engine.md)
- [Alert API](2026-05-19-alert-api.md)
