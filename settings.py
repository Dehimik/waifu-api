from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    environment: str = "development"

    # replaced with upstash redis url
    redis_url: str = "redis://localhost:6379"
    redis_queue_key: str = "cat_data_queue"
    redis_min_size: int = 2

    database_url: str | None = None

    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_username: str = "devlad"
    pg_password: str = "postgres"
    pg_db_name: str = "postgres"
    pg_db_driver: str = "postgresql"

    model_config = ConfigDict(
        extra="allow",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @property
    def final_postgres_url(self) -> str:
        if self.database_url:
            url = self.database_url
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            return url

        return (
            f"{self.pg_db_driver}+asyncpg://{self.pg_username}:{self.pg_password}@"
            f"{self.pg_host}:{self.pg_port}/{self.pg_db_name}"
        )


settings = Settings()