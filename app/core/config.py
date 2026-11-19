from functools import lru_cache
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = Field(min_length=1)
    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0)
    BCRYPT_SALT_ROUNDS: int = Field(default=12, ge=4, le=31)
    CORS_ORIGINS: list[str] = Field(default_factory=list)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        parsed_url = urlsplit(value)
        if parsed_url.scheme.split("+", maxsplit=1)[0] not in {
            "postgresql",
            "mysql",
            "sqlite",
        }:
            raise ValueError("DATABASE_URL must use PostgreSQL, MySQL, or SQLite")
        return value

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("JWT_SECRET_KEY must not be empty")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
