# Frontend Service — Risk Dashboard

## 職責

系統主頁（`/dashboard`），讓醫護人員一眼掌握：目前有幾個高風險病患、有多少未處理的 Alert、整體情緒趨勢。

## 頁面佈局

```
┌────────────────────────────────────────────────────────────┐
│  Cancer Emotion Monitor                    Dr. Chen ▾ 登出  │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 🔴 HIGH  │  │ 🟠 MEDIUM│  │ 未處理   │  │ 今日新增  │  │
│  │    7     │  │   12     │  │ Alert 9  │  │ 記錄 248  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                             │
│  高風險病患（需立即關注）                           全部查看 →  │
│  ┌────────────────────────────────────────────────────┐   │
│  │ user_a3f2  │ 連續11天 │ 均值 0.88 │ 🔴 HIGH │ 查看 │   │
│  │ user_b7c1  │ 連續 9天 │ 均值 0.82 │ 🔴 HIGH │ 查看 │   │
│  │ user_d9e4  │ 連續 7天 │ 均值 0.81 │ 🔴 HIGH │ 查看 │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  未處理 Alert                                    全部查看 →  │
│  ┌────────────────────────────────────────────────────┐   │
│  │ 🔴 user_a3f2 │ 連續11天情緒負面... │ 3小時前 │ 確認 │   │
│  │ 🔴 user_b7c1 │ 情緒分數急降45%... │ 5小時前 │ 確認 │   │
│  └────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

## 資料來源

```
GET /api/v1/dashboard/summary
GET /api/v1/dashboard/high-risk-patients
GET /api/v1/alerts?status=OPEN&size=5&sort=createdAt,desc
```

## `GET /api/v1/dashboard/summary` 回傳格式

```json
{
  "highRiskCount": 7,
  "mediumRiskCount": 12,
  "openAlertsCount": 9,
  "todayNewRecords": 248,
  "updatedAt": "2026-05-19T10:00:00Z"
}
```

## `GET /api/v1/dashboard/high-risk-patients` 回傳格式

```json
[
  {
    "patientId": "uuid",
    "externalUserId": "user_a3f2",
    "consecutiveNegativeDays": 11,
    "rollingAvg7d": 0.88,
    "riskLevel": "HIGH",
    "lastSeenAt": "2026-05-19T09:00:00Z"
  }
]
```

## 統計卡（Summary Cards）元件

```tsx
function SummaryCard({ label, value, color, onClick }) {
  return (
    <div
      className={`p-4 rounded-lg border-2 cursor-pointer hover:shadow-md ${color}`}
      onClick={onClick}
    >
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
    </div>
  );
}
```

點擊「HIGH 7」→ 跳轉到 `/patients?riskLevel=HIGH`
點擊「未處理 Alert 9」→ 跳轉到 `/alerts?status=OPEN`

## 自動刷新

Dashboard 每 60 秒自動重新拉資料（React Query `refetchInterval`），不需要手動重新整理頁面。

## 高風險病患列表

| 欄位 | 說明 |
|---|---|
| 匿名 ID | `externalUserId` 前 8 字元，例如 `user_a3f2` |
| 連續負面天數 | 用紅色數字顯示 |
| 7 天均值 | 百分比顯示 |
| 風險等級 | `RiskBadge` 元件 |
| 操作 | 「查看」→ 跳轉病患詳情頁 |

不顯示任何可識別個人的資訊（無真實姓名、Reddit 帳號等）。

## 相關 Spec

- [Service Overview](2026-05-19-service-overview.md)
- [Alert Management](2026-05-19-alert-management.md)
- [Trajectory Chart](2026-05-19-trajectory-chart.md)
