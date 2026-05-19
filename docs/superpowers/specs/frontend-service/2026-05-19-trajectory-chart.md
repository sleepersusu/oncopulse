# Frontend Service — Emotion Trajectory Chart

## 職責

在病患詳情頁（`/patients/:id`）顯示情緒隨時間變化的折線圖，是系統最核心的視覺化元件。

## 資料來源

```
GET /api/v1/patients/:id/emotion-trajectory?days=30&granularity=daily
```

## 元件設計

```tsx
// components/EmotionTrajectoryChart.tsx

import { LineChart, Line, XAxis, YAxis, CartesianGrid,
         Tooltip, Legend, ReferenceLine, ResponsiveContainer } from "recharts";

interface DataPoint {
  date: string;
  avgNegativeScore: number;
  avgPositiveScore: number;
  recordCount: number;
  dominantEmotion: string;
}

interface Props {
  patientId: string;
  days?: number;
}

export function EmotionTrajectoryChart({ patientId, days = 30 }: Props) {
  const { data, isLoading } = useQuery({
    queryKey: ["trajectory", patientId, days],
    queryFn: () => fetchTrajectory(patientId, days),
    refetchInterval: 60_000,  // 每分鐘自動更新
  });

  if (isLoading) return <ChartSkeleton />;

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">情緒軌跡（過去 {days} 天）</h3>
        <DaysSelector value={days} onChange={setDays} options={[7, 14, 30, 90]} />
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data?.dataPoints}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tickFormatter={formatDate} />
          <YAxis domain={[0, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />

          {/* 負面情緒分數 — 主線 */}
          <Line
            type="monotone"
            dataKey="avgNegativeScore"
            stroke="#ef4444"
            strokeWidth={2}
            name="負面情緒"
            dot={false}
            activeDot={{ r: 6 }}
          />

          {/* 正面情緒分數 */}
          <Line
            type="monotone"
            dataKey="avgPositiveScore"
            stroke="#22c55e"
            strokeWidth={2}
            name="正面情緒"
            dot={false}
          />

          {/* 高風險閾值線 */}
          <ReferenceLine y={0.8} stroke="#ef4444" strokeDasharray="4 4"
            label={{ value: "HIGH 閾值", position: "right", fill: "#ef4444" }} />
          <ReferenceLine y={0.65} stroke="#f97316" strokeDasharray="4 4"
            label={{ value: "MEDIUM 閾值", position: "right", fill: "#f97316" }} />
        </LineChart>
      </ResponsiveContainer>

      {/* 軌跡摘要統計 */}
      <TrajectorySummary summary={data?.summary} />
    </div>
  );
}
```

## TrajectorySummary 元件

顯示在圖表下方，給醫護快速掌握關鍵數值：

```
┌─────────────────────────────────────────────────────┐
│  7天均值  │  連續負面  │  較基準下降  │  風險等級    │
│   82%    │   9 天    │   45.2%    │  🔴 HIGH    │
└─────────────────────────────────────────────────────┘
```

```tsx
function TrajectorySummary({ summary }) {
  return (
    <div className="grid grid-cols-4 gap-4 mt-4 p-4 bg-gray-50 rounded-lg">
      <Stat label="7天負面均值" value={`${(summary.rollingAvg7d * 100).toFixed(1)}%`} />
      <Stat label="連續負面天數" value={`${summary.consecutiveNegativeDays} 天`} />
      <Stat label="較基準下降" value={`${summary.scoreDropPct.toFixed(1)}%`}
            highlight={summary.scoreDropPct > 40} />
      <RiskBadge level={summary.currentRiskLevel} size="lg" />
    </div>
  );
}
```

## CustomTooltip

滑鼠懸停時顯示該日詳情：

```
2026-05-19
負面情緒：82%
正面情緒：8%
貼文數：5 則
```

## 空狀態處理

| 情況 | 顯示 |
|---|---|
| 資料點 < 3 | "資料不足，需至少 3 天的紀錄才能顯示軌跡" |
| API 錯誤 | "載入失敗，請重新整理" + 重試按鈕 |
| 無任何資料 | "此用戶尚無情緒紀錄" |

## 相關 Spec

- [Service Overview](2026-05-19-service-overview.md)
- [Emotion Record API](../spring-boot-service/2026-05-19-emotion-record-api.md)
