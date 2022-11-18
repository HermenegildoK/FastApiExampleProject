import logging
import os.path
import re
from functools import lru_cache
from typing import Optional

from pydantic import (
    BaseModel,
    BaseSettings,
    ConstrainedStr,
    PostgresDsn,
    root_validator,
    validator,
)


class PrefixString(ConstrainedStr):
    strip_whitespace = True
    regex = re.compile(r"^(/\w+)*[^/]$|^$")


class LoggingConfiguration(BaseModel):
    LOG_PATH: Optional[str] = None
    LOG_TO_FILE: bool = False
    LOG_TO_LEVEL_FILES: bool = False
    JSON_LOG_FILE: Optional[str] = None
    LOG_SQL: bool = True
    LOG_JSON: bool = False
    MIN_LOG_LEVEL: int = logging.DEBUG

    @validator("LOG_PATH")
    def validate_log_path(cls, value):
        if value and not os.path.isdir(value):
            raise ValueError(f"'{value} is not valid folder")
        return value

    @validator("MIN_LOG_LEVEL")
    def validate_min_log_level(cls, value):
        if value is None:
            return logging.DEBUG
        if value not in (
            logging.CRITICAL,
            logging.FATAL,
            logging.ERROR,
            logging.WARNING,
            logging.WARN,
            logging.INFO,
            logging.DEBUG,
            logging.NOTSET,
        ):
            raise ValueError(f"'{value}' is not a valid logging level.")
        return value

    @validator("LOG_TO_FILE")
    def validate_log_to_file(cls, v, values, **kwargs):
        if v and not values.get("LOG_PATH"):
            raise ValueError("LOG_PATH must be set when LOG_TO_FILE=True")
        return v

    @validator("LOG_JSON")
    def validate_log_json(cls, v, values, **kwargs):

        if v and (
            not values.get("JSON_LOG_FILE")
            or not values.get("LOG_TO_FILE")
            or not values.get("LOG_PATH")
        ):
            raise ValueError(f"JSON_LOG_FILE must be set when LOG_JSON=True, {values}")
        return v


class Settings(BaseSettings):
    API_PREFIX: PrefixString
    USE_DATABASE: bool
    DATABASE_URL: Optional[PostgresDsn] = None
    APP_NAME: str = "FastAPI example"
    LOGGING: LoggingConfiguration = LoggingConfiguration()

    @root_validator()
    def validate(cls, values):
        if values.get("USE_DATABASE") and not values.get("DATABASE_URL"):
            raise ValueError("DATABASE_URL must be set when USE_DATABASE=True")
        return values

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return Settings()
