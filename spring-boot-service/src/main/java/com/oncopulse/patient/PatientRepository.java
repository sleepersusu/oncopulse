package com.oncopulse.patient;

import com.oncopulse.common.RiskLevel;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface PatientRepository extends JpaRepository<Patient, UUID> {

    Optional<Patient> findByExternalUserId(String externalUserId);

    boolean existsByExternalUserId(String externalUserId);

    Page<Patient> findByCurrentRiskLevel(RiskLevel riskLevel, Pageable pageable);

    Page<Patient> findByIsActiveTrue(Pageable pageable);

    Page<Patient> findByCurrentRiskLevelAndIsActiveTrue(RiskLevel riskLevel, Pageable pageable);
}
