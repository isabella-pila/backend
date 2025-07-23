import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar


class Settings(BaseSettings):
    POSTGRES_USER: str = "petfituser"
    POSTGRES_PASSWORD: str = "petfitpass"
    POSTGRES_DB: str = "petfitdb"
    POSTGRES_PORT: int = 5432
    POSTGRES_HOST: str = "db"

    DOCKER_ENV: int = 0

    DATABASE_URL: str = "postgresql+asyncpg://petfituser:petfitpass@db:5432/petfitdb"
    DATABASE_URL_ALEMBIC: str = "postgresql+psycopg2://petfituser:petfitpass@db:5432/petfitdb"
    DATABASE_URL_TEST: str = "postgresql+asyncpg://test_user:test_password@db_test:5432/petfit_test"

    SECRET_KEY: str = "myjwtsecret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env", extra="ignore"
    )


settings = Settings()