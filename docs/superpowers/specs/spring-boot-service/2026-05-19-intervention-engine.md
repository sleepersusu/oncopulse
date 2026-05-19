# Spring Boot Service — Intervention Engine

## 職責

根據病患的最新風險等級，決定是否建立 Alert。核心業務邏輯，確保介入觸發有規則、可追蹤、不重複。

## 觸發時機

每次 `POST /api/v1/emotion-records/batch` 處理完成後，對本批次中風險等級有變化的病患呼叫 InterventionEngine。

## 核心規則

```java
@Service
public class InterventionEngine {

    // 同一病患的 HIGH risk，24 小時內只觸發一次 Alert，避免 Alert 洪水
    private static final Duration HIGH_RISK_COOLDOWN = Duration.ofHours(24);
    // MEDIUM risk，72 小時內只觸發一次
    private static final Duration MEDIUM_RISK_COOLDOWN = Duration.ofHours(72);

    public void evaluate(Patient patient, RiskLevel newRiskLevel) {
        if (newRiskLevel == RiskLevel.LOW || newRiskLevel == RiskLevel.INSUFFICIENT_DATA) {
            return;  // 不觸發
        }

        Duration cooldown = switch (newRiskLevel) {
            case HIGH -> HIGH_RISK_COOLDOWN;
            case MEDIUM -> MEDIUM_RISK_COOLDOWN;
            default -> throw new IllegalStateException();
        };

        boolean recentAlertExists = alertRepository
            .existsByPatientIdAndRiskLevelAndCreatedAtAfter(
                patient.getId(),
                newRiskLevel.name(),
                Instant.now().minus(cooldown)
            );

        if (!recentAlertExists) {
            createAlert(patient, newRiskLevel);
        }
    }

    private void createAlert(Patient patient, RiskLevel riskLevel) {
        String reason = buildTriggerReason(patient, riskLevel);
        Alert alert = Alert.builder()
            .patientId(patient.getId())
            .riskLevel(riskLevel.name())
            .triggerReason(reason)
            .status(AlertStatus.OPEN)
            .build();
        alertRepository.save(alert);
    }
}
```

## 觸發原因文字（`trigger_reason`）

系統自動產生給醫護人員看的說明文字，例如：

```
HIGH RISK: 連續 9 天情緒負面（分數均值 0.82），
較 30 天前基準下降 45.2%。
來源：reddit | 資料點數：42 筆 | 最後發文：2026-05-19
```

## 風險等級升降邏輯

```
舊等級    新等級    動作
LOW   →  HIGH     建立 HIGH Alert（若冷卻期未到期）
LOW   →  MEDIUM   建立 MEDIUM Alert（若冷卻期未到期）
MEDIUM→  HIGH     建立 HIGH Alert（MEDIUM Alert 保持 OPEN，不自動關閉）
HIGH  →  MEDIUM   不觸發（風險下降，現有 HIGH Alert 由醫護手動 resolve）
HIGH  →  LOW      不觸發（同上）
```

## 不直接對病患發送任何通知

引擎只建立 Alert 記錄到資料庫。由醫護人員在 Dashboard 看到 Alert 後，**由人決定**如何回應（致電、安排諮詢、發訊息等）。系統不自動傳訊給病患，避免造成二次心理傷害。

## Alert 狀態流程

```
OPEN ──→ ACKNOWLEDGED ──→ RESOLVED
          (醫護已看到)      (醫護已處理)
```

- `ACKNOWLEDGED`：醫護點擊確認已看到，記錄 `acknowledged_by` 與 `acknowledged_at`
- `RESOLVED`：醫護確認已採取行動，可附加 `notes`

## 相關 Spec

- [Alert API](2026-05-19-alert-api.md)
- [Risk Scoring](../python-nlp-service/2026-05-19-risk-scoring.md)
