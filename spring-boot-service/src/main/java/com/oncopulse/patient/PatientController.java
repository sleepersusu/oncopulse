package com.oncopulse.patient;

import com.oncopulse.common.RiskLevel;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/patients")
@RequiredArgsConstructor
public class PatientController {

    private final PatientService service;

    @GetMapping
    public Page<PatientDto.Response> list(
            @RequestParam(required = false) RiskLevel riskLevel,
            @PageableDefault(size = 20, sort = "lastSeenAt") Pageable pageable
    ) {
        return service.findAll(riskLevel, pageable);
    }

    @GetMapping("/{id}")
    public PatientDto.Response get(@PathVariable UUID id) {
        return service.findById(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public PatientDto.Response create(@RequestBody PatientDto.CreateRequest req) {
        return service.create(req);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deactivate(@PathVariable UUID id) {
        service.deactivate(id);
    }
}
