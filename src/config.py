from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL : str
    SECRET_KEY : str
    ALGORITHM : str
    MAIL_USERNAME : str
    MAIL_PASSWORD : str
    MAIL_SERVER : str
    MAIL_PORT : int
    MAIL_FROM_EMAIL : str
    MAIL_FROM_NAME : str
    DOMAIN : str
    REDIS_URL : str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

Config = Settings()

# Celery Configuration
broker_url = Config.REDIS_URL
result_backend = Config.REDIS_URL
