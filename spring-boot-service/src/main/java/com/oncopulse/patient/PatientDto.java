package com.oncopulse.patient;

import com.oncopulse.common.RiskLevel;
import lombok.Builder;

import java.time.Instant;
import java.util.UUID;

public class PatientDto {

    @Builder
    public record Response(
            UUID id,
            String externalUserId,
            String source,
            Instant firstSeenAt,
            Instant lastSeenAt,
            RiskLevel currentRiskLevel,
            boolean isActive,
            Instant createdAt
    ) {
        static Response from(Patient p) {
            return Response.builder()
                    .id(p.getId())
                    .externalUserId(p.getExternalUserId())
                    .source(p.getSource())
                    .firstSeenAt(p.getFirstSeenAt())
                    .lastSeenAt(p.getLastSeenAt())
                    .currentRiskLevel(p.getCurrentRiskLevel())
                    .isActive(p.isActive())
                    .createdAt(p.getCreatedAt())
                    .build();
        }
    }

    public record CreateRequest(
            String externalUserId,
            String source
    ) {}
}
