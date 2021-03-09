from enum import IntEnum

from pydantic import ConstrainedInt


class DataTypeEnum(IntEnum):
    SIMPLE = 1
    COMPLEX = 2
    ULTRA_SUPRA_COOL = 666


class DataCounterLimits(IntEnum):
    MIN = 90
    MAX = 99
    STEP = 2


class CountLimit(ConstrainedInt):
    strict = True
    ge = DataCounterLimits.MIN
    le = DataCounterLimits.MAX
