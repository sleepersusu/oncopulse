# Frontend Service — Alert Management

## 職責

提供醫護人員查看、確認（acknowledge）、解決（resolve）Alert 的操作介面。

## 頁面：Alert 列表（`/alerts`）

```
┌────────────────────────────────────────────────────────────┐
│  Alert 管理                                                  │
│                                                             │
│  狀態：[OPEN ▾]   風險：[全部 ▾]   日期：[本週 ▾]            │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ 🔴 HIGH  user_a3f2                        3 小時前  │   │
│  │ 連續 11 天情緒負面，7天均值 0.88，較基準下降 52%      │   │
│  │                              [確認已看到]  [查看詳情] │   │
│  ├────────────────────────────────────────────────────┤   │
│  │ 🔴 HIGH  user_b7c1                        5 小時前  │   │
│  │ 情緒分數急降 45.2%，連續 9 天負面                    │   │
│  │                              [確認已看到]  [查看詳情] │   │
│  ├────────────────────────────────────────────────────┤   │
│  │ 🟠 MEDIUM user_c2d8                       1 天前   │   │
│  │ 連續 4 天情緒負面，發文頻率減少 60%                  │   │
│  │                              [確認已看到]  [查看詳情] │   │
│  └────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

## 頁面：Alert 詳情（`/alerts/:id`）

```
┌────────────────────────────────────────────────────────────┐
│  ← 返回  Alert 詳情                                          │
│                                                             │
│  🔴 HIGH RISK — user_a3f2             建立於 3 小時前        │
│  狀態：OPEN                                                  │
│                                                             │
│  觸發原因                                                    │
│  ┌────────────────────────────────────────────────────┐   │
│  │ 連續 11 天情緒負面（分數均值 0.88），                 │   │
│  │ 較 30 天前基準下降 52.1%。                           │   │
│  │ 來源：reddit | 資料點數：67 筆 | 最後發文：2小時前   │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  病患情緒軌跡（過去 14 天）                                   │
│  [EmotionTrajectoryChart 嵌入]                               │
│                                                             │
│  操作                                                        │
│  ┌────────────────────────────────────────────────────┐   │
│  │  [✓ 確認已看到]                                     │   │
│  └────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

確認後切換為 ACKNOWLEDGED 狀態，顯示 Resolve 按鈕與備註輸入框：

```
┌────────────────────────────────────────────────────────────┐
│  狀態：ACKNOWLEDGED — 已由 Dr. Chen 確認（10 分鐘前）         │
│                                                             │
│  處理備註                                                    │
│  ┌────────────────────────────────────────────────────┐   │
│  │ 已電話聯繫個案管理師，安排本週心理評估...            │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  [✓ 標記為已解決]                                            │
└────────────────────────────────────────────────────────────┘
```

## 前端操作邏輯

```tsx
// Acknowledge
async function acknowledgeAlert(alertId: string) {
  const user = useAuthStore.getState().displayName;
  await apiClient.put(`/api/v1/alerts/${alertId}/acknowledge`, {
    acknowledgedBy: user,
  });
  queryClient.invalidateQueries(["alerts"]);
  queryClient.invalidateQueries(["dashboard"]);
}

// Resolve
async function resolveAlert(alertId: string, notes: string) {
  await apiClient.put(`/api/v1/alerts/${alertId}/resolve`, { notes });
  queryClient.invalidateQueries(["alerts"]);
  queryClient.invalidateQueries(["dashboard"]);
}
```

`invalidateQueries` 確保 Dashboard 統計數字同步更新，不需要手動刷頁。

## RiskBadge 元件

跨頁面共用的風險等級標籤：

```tsx
const CONFIG = {
  HIGH:   { label: "HIGH",   bg: "bg-red-100",    text: "text-red-700",    dot: "bg-red-500"    },
  MEDIUM: { label: "MEDIUM", bg: "bg-orange-100", text: "text-orange-700", dot: "bg-orange-500" },
  LOW:    { label: "LOW",    bg: "bg-green-100",  text: "text-green-700",  dot: "bg-green-500"  },
};

export function RiskBadge({ level, size = "sm" }) {
  const c = CONFIG[level] ?? CONFIG.LOW;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full ${c.bg} ${c.text}`}>
      <span className={`w-2 h-2 rounded-full ${c.dot}`} />
      {c.label}
    </span>
  );
}
```

## 相關 Spec

- [Service Overview](2026-05-19-service-overview.md)
- [Alert API](../spring-boot-service/2026-05-19-alert-api.md)
- [Risk Dashboard](2026-05-19-risk-dashboard.md)
