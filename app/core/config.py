from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    RABBITMQ_URL: str
    REDIS_URL: str
    GF_SECURITY_ADMIN_PASSWORD:str

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()