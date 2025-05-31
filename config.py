from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL

PROJECT_DIR = Path(__file__).parent.parent.parent


class Database(BaseModel):
    hostname: str = "127.0.0.1"
    username: str = "postgres"
    password: SecretStr = "postgres"
    port: int = 5432
    db: str = "paydb"


class App(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class Logger(BaseModel):
    path: str = "resources/logs"
    level: str = "DEBUG"


class Monopay(BaseModel):
    token: str


class Settings(BaseSettings):
    database: Database
    app: App
    logger: Logger
    monopay: Monopay

    @computed_field
    @property
    def sqlalchemy_database_uri(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.database.username,
            password=self.database.password.get_secret_value(),
            host=self.database.hostname,
            port=self.database.port,
            database=self.database.db,
        )

    model_config = SettingsConfigDict(
        env_file=f"{PROJECT_DIR}/.env",
        case_sensitive=False,
        env_nested_delimiter="__",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
