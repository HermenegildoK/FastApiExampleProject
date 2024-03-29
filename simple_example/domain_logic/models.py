from typing import Optional

from pydantic import BaseModel, ConfigDict, PositiveInt

from simple_example.domain_logic.consts import CountLimit, DataTypeEnum

# These are models you expose to outside world


class InputModel(BaseModel):
    name: str
    data_type: DataTypeEnum
    count: CountLimit
    model_config = ConfigDict(use_enum_values=True)


class DataEntity(InputModel):
    id: PositiveInt
    model_config = ConfigDict(use_enum_values=True)


class Filters(BaseModel):
    search_string: Optional[str] = None
    data_type: Optional[DataTypeEnum] = None
    count_upper_limit: Optional[CountLimit] = None
    count_lower_limit: Optional[CountLimit] = None
    model_config = ConfigDict(use_enum_values=True)
