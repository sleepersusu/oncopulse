CREATE TABLE emotion_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID         NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    source          VARCHAR(20)  NOT NULL,
    post_id         VARCHAR(64)  NOT NULL,
    text_snippet    TEXT,
    posted_at       TIMESTAMP WITH TIME ZONE NOT NULL,
    emotion_label   VARCHAR(20)  NOT NULL,
    emotion_score   DECIMAL(5,4) NOT NULL,
    positive_score  DECIMAL(5,4),
    neutral_score   DECIMAL(5,4),
    negative_score  DECIMAL(5,4),
    risk_level      VARCHAR(20)  NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_post UNIQUE (source, post_id)
);

CREATE INDEX idx_emotion_records_patient_id ON emotion_records(patient_id);
CREATE INDEX idx_emotion_records_posted_at  ON emotion_records(posted_at DESC);
CREATE INDEX idx_emotion_records_risk_level ON emotion_records(risk_level);
