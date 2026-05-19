# Frontend Service — Service Overview

## 職責

提供醫護人員使用的臨床 Dashboard：查看病患情緒軌跡、管理 Alert、追蹤高風險病患清單。

## 技術棧

| 項目 | 選擇 |
|---|---|
| 框架 | React 18 + TypeScript |
| 路由 | React Router v6 |
| 狀態管理 | Zustand（輕量，避免 Redux 過度工程）|
| HTTP | Axios + React Query（快取與自動重新整理）|
| 圖表 | Recharts（情緒軌跡折線圖）|
| UI 元件庫 | shadcn/ui + Tailwind CSS |
| 建置工具 | Vite |
| 容器 | Docker + Nginx |

## 頁面結構

```
/login                    ← 登入頁
/dashboard                ← 主頁，總覽統計 + 高風險病患列表
/patients                 ← 病患清單（可搜尋、過濾）
/patients/:id             ← 單一病患詳情 + 情緒軌跡圖
/alerts                   ← Alert 管理列表
/alerts/:id               ← 單一 Alert 詳情 + 操作
```

## 與 Spring Boot 通訊

所有 API 呼叫都打 Spring Boot，無直接呼叫 Python Service。

```typescript
// api/client.ts
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// 自動帶入 JWT
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
```

## 環境變數

```env
VITE_API_BASE_URL=http://localhost:8080
```

## 模組結構

```
frontend-service/
├── src/
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── PatientList.tsx
│   │   ├── PatientDetail.tsx
│   │   ├── AlertList.tsx
│   │   └── AlertDetail.tsx
│   │
│   ├── components/
│   │   ├── EmotionTrajectoryChart.tsx  ← 折線圖元件
│   │   ├── RiskBadge.tsx               ← HIGH/MEDIUM/LOW 標籤
│   │   ├── AlertCard.tsx
│   │   └── PatientCard.tsx
│   │
│   ├── api/
│   │   ├── client.ts
│   │   ├── patients.ts
│   │   ├── emotionRecords.ts
│   │   └── alerts.ts
│   │
│   ├── stores/
│   │   └── authStore.ts
│   │
│   └── types/
│       └── index.ts                    ← 共用 TypeScript 型別
```

## 相關 Spec

- [Trajectory Chart](2026-05-19-trajectory-chart.md)
- [Risk Dashboard](2026-05-19-risk-dashboard.md)
- [Alert Management](2026-05-19-alert-management.md)
