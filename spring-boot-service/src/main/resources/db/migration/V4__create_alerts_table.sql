CREATE TABLE alerts (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id       UUID         NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    risk_level       VARCHAR(20)  NOT NULL,
    trigger_reason   TEXT         NOT NULL,
    status           VARCHAR(20)  NOT NULL DEFAULT 'OPEN',
    acknowledged_by  VARCHAR(100),
    acknowledged_at  TIMESTAMP WITH TIME ZONE,
    resolved_at      TIMESTAMP WITH TIME ZONE,
    notes            TEXT,
    created_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_alerts_patient_id ON alerts(patient_id);
CREATE INDEX idx_alerts_status     ON alerts(status);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);
