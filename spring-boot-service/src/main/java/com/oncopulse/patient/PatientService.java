package com.oncopulse.patient;

import com.oncopulse.common.RiskLevel;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.time.Instant;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class PatientService {

    private final PatientRepository repo;

    @Transactional(readOnly = true)
    public Page<PatientDto.Response> findAll(RiskLevel riskLevel, Pageable pageable) {
        Page<Patient> page = riskLevel != null
                ? repo.findByCurrentRiskLevelAndIsActiveTrue(riskLevel, pageable)
                : repo.findByIsActiveTrue(pageable);
        return page.map(PatientDto.Response::from);
    }

    @Transactional(readOnly = true)
    public PatientDto.Response findById(UUID id) {
        return repo.findById(id)
                .map(PatientDto.Response::from)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Patient not found"));
    }

    @Transactional
    public PatientDto.Response create(PatientDto.CreateRequest req) {
        if (repo.existsByExternalUserId(req.externalUserId())) {
            throw new ResponseStatusException(HttpStatus.CONFLICT,
                    "Patient with this externalUserId already exists");
        }
        Patient patient = Patient.builder()
                .externalUserId(req.externalUserId())
                .source(req.source())
                .firstSeenAt(Instant.now())
                .lastSeenAt(Instant.now())
                .build();
        return PatientDto.Response.from(repo.save(patient));
    }

    @Transactional
    public PatientDto.Response deactivate(UUID id) {
        Patient patient = repo.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Patient not found"));
        patient.setActive(false);
        return PatientDto.Response.from(repo.save(patient));
    }

    // Called by InterventionEngine after emotion records are processed
    @Transactional
    public void updateRiskLevel(String externalUserId, RiskLevel newLevel, Instant lastSeenAt) {
        repo.findByExternalUserId(externalUserId).ifPresent(p -> {
            p.setCurrentRiskLevel(newLevel);
            p.setLastSeenAt(lastSeenAt);
            repo.save(p);
        });
    }

    // Called by EmotionRecordService when a new record arrives for an unknown user
    @Transactional
    public Patient findOrCreate(String externalUserId, String source, Instant seenAt) {
        return repo.findByExternalUserId(externalUserId).orElseGet(() -> {
            Patient p = Patient.builder()
                    .externalUserId(externalUserId)
                    .source(source)
                    .firstSeenAt(seenAt)
                    .lastSeenAt(seenAt)
                    .build();
            return repo.save(p);
        });
    }
}
