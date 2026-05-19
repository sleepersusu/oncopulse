CREATE TABLE patients (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_user_id   VARCHAR(64)  NOT NULL UNIQUE,
    source             VARCHAR(20)  NOT NULL,
    first_seen_at      TIMESTAMP WITH TIME ZONE NOT NULL,
    last_seen_at       TIMESTAMP WITH TIME ZONE NOT NULL,
    current_risk_level VARCHAR(20)  NOT NULL DEFAULT 'LOW',
    is_active          BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at         TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_patients_external_user_id ON patients(external_user_id);
CREATE INDEX idx_patients_risk_level       ON patients(current_risk_level);
