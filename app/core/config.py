from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USER: str = "root"
    DB_PASSWORD: str = "password1234"
    DB_HOST: str = "localhost"
    DB_PORT: str = "3306"
    DB_NAME: str = "ai_health"

    USE_SQLITE: bool = False  # true로 설정하면 MySQL 없이 SQLite로 실행

    JWT_SECRET_KEY: str = "change-this-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }


settings = Settings()
