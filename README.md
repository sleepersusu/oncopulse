# OncoPulse

> Cancer Patient Emotion Trajectory Monitoring & Clinical Intervention System

OncoPulse is a research system that detects emotional deterioration in cancer patients through NLP analysis of text data, and triggers clinical intervention alerts before crisis occurs.

## Motivation

Based on Hong et al. (*Cancer*, 2026): 10.6% of cancer patients develop a new mental health disorder within one year of diagnosis, with significantly higher all-cause mortality (HR 1.51). Current clinical workflows lack proactive detection. OncoPulse addresses this gap.

## Architecture

Three microservices:

| Service | Stack | Role |
|---|---|---|
| `python-nlp-service` | Python 3.11 + FastAPI | Data collection, emotion classification, trajectory modeling, risk scoring |
| `spring-boot-service` | Java 21 + Spring Boot 3 | Persistence, intervention rule engine, REST API |
| `frontend-service` | React 18 + TypeScript | Clinical dashboard, alert management |

**Database:** PostgreSQL 16

## Research Alignment

This project directly extends research from UC Berkeley / UCSF Computational Precision Health:
- **Julian Hong, MD** (UCSF) — Cancer × mental health comorbidity
- **Irene Chen, PhD** (Berkeley CPH) — Trustworthy clinical AI
- **Adrian Aguilera, PhD** (Berkeley dHEAL) — Digital mental health interventions

## Data Sources

- **Phase 1:** Reddit r/cancer (public API) — model development & validation
- **Phase 2:** MIMIC-III (PhysioNet) — clinical notes validation
- **Phase 3:** Consented pilot participants — intervention research

## Ethics

- Public data used only for model training, never for individual intervention
- Clinical intervention only for patients with informed consent
- HIGH risk alerts notify clinicians only — system never contacts patients directly
- All user identifiers hashed (SHA-256), no plaintext usernames stored

## Specs

Full design specifications: [`docs/superpowers/specs/`](docs/superpowers/specs/)

## License

Research use only. Not for clinical deployment without IRB approval.
