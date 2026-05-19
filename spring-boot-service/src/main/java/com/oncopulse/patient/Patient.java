package com.oncopulse.patient;

import com.oncopulse.common.RiskLevel;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "patients")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Patient {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "external_user_id", nullable = false, unique = true, length = 64)
    private String externalUserId;

    @Column(nullable = false, length = 20)
    private String source;

    @Column(name = "first_seen_at", nullable = false)
    private Instant firstSeenAt;

    @Column(name = "last_seen_at", nullable = false)
    private Instant lastSeenAt;

    @Enumerated(EnumType.STRING)
    @Column(name = "current_risk_level", nullable = false, length = 20)
    @Builder.Default
    private RiskLevel currentRiskLevel = RiskLevel.LOW;

    @Column(name = "is_active", nullable = false)
    @Builder.Default
    private boolean isActive = true;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;

    @PrePersist
    void onCreate() {
        Instant now = Instant.now();
        this.createdAt = now;
        this.updatedAt = now;
        if (this.firstSeenAt == null) this.firstSeenAt = now;
        if (this.lastSeenAt == null)  this.lastSeenAt  = now;
    }
}
