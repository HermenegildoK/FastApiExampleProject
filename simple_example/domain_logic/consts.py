from enum import IntEnum

from pydantic import Field
from typing_extensions import Annotated


class DataTypeEnum(IntEnum):
    SIMPLE = 1
    COMPLEX = 2
    ULTRA_SUPRA_COOL = 666


class DataCounterLimits(IntEnum):
    MIN = 0
    MAX = 99
    STEP = 2


CountLimit = Annotated[
    int,
    Field(strict=True, ge=DataCounterLimits.MIN.value, le=DataCounterLimits.MAX.value),
]
