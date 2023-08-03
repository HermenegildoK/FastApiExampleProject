import logging
import os.path
from functools import lru_cache
from typing import Optional

from pydantic import BaseModel, Field, PostgresDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingConfiguration(BaseModel):
    LOG_PATH: Optional[str] = None
    LOG_TO_FILE: bool = False
    LOG_TO_LEVEL_FILES: bool = False
    JSON_LOG_FILE: Optional[str] = None
    LOG_SQL: bool = True
    LOG_JSON: bool = False
    MIN_LOG_LEVEL: int = logging.DEBUG

    @field_validator("LOG_PATH")
    @classmethod
    def validate_log_path(cls, v):
        if v and not os.path.isdir(v):
            raise ValueError(f"'{v} is not valid folder")
        return v

    @field_validator("MIN_LOG_LEVEL")
    @classmethod
    def validate_min_log_level(cls, v):
        if v is None:
            return logging.DEBUG
        if v not in (
            logging.CRITICAL,
            logging.FATAL,
            logging.ERROR,
            logging.WARNING,
            logging.WARN,
            logging.INFO,
            logging.DEBUG,
            logging.NOTSET,
        ):
            raise ValueError(f"'{v}' is not a valid logging level.")
        return v

    @model_validator(mode="after")
    def validate_log_json(self):
        if self.LOG_JSON and (not self.LOG_TO_FILE or not self.LOG_PATH):
            raise ValueError("JSON_LOG_FILE must be set when LOG_JSON=True")
        if self.LOG_TO_FILE and not self.LOG_PATH:
            raise ValueError("LOG_PATH must be set when LOG_TO_FILE=True")
        return self


class Settings(BaseSettings):
    API_PREFIX: str = Field(strict=True, pattern=r"^(/\w+)*[^/]$|^$")
    USE_DATABASE: bool
    DATABASE_URL: Optional[PostgresDsn] = None
    APP_NAME: str = "FastAPI example"
    LOGGING: LoggingConfiguration = LoggingConfiguration()

    @model_validator(mode="before")
    @classmethod
    def validate(cls, data):
        if (
            isinstance(data, dict)
            and data.get("USE_DATABASE")
            and not data.get("DATABASE_URL")
        ):
            raise ValueError("DATABASE_URL must be set when USE_DATABASE=True")
        return data

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings():
    return Settings()
