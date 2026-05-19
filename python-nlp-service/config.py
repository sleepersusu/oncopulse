from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # HuggingFace
    hf_token: str = ""

    # Reddit
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "oncopulse/0.1"
    reddit_hash_salt: str = "change_me"

    # Spring Boot
    spring_boot_url: str = "http://localhost:8080"
    nlp_service_api_key: str = "change_me"

    # NLP Model
    emotion_model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"

    # Risk thresholds
    risk_high_consecutive_days: int = 7
    risk_high_drop_pct: float = 40.0
    risk_high_avg_threshold: float = 0.80
    risk_medium_consecutive_days: int = 3
    risk_medium_drop_pct: float = 20.0
    risk_medium_avg_threshold: float = 0.65
    risk_medium_freq_drop: float = 0.50

    # Scheduler
    push_interval_minutes: int = 60


settings = Settings()
