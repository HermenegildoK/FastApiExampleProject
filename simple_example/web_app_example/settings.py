import re
from functools import lru_cache
from typing import Optional

from pydantic import (
    BaseModel,
    BaseSettings,
    ConstrainedStr,
    PostgresDsn,
    root_validator, validator,
)


class PrefixString(ConstrainedStr):
    strip_whitespace = True
    regex = re.compile(r"^(/\w+)*[^/]$|^$")


class Settings(BaseSettings):
    API_PREFIX: PrefixString
    USE_DATABASE: bool
    DATABASE_URL: Optional[PostgresDsn] = None

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
