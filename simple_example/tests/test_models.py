import pytest

from simple_example.domain_logic.consts import DataCounterLimits, DataTypeEnum
from simple_example.domain_logic.models import Filters, InputModel

# your models are you contracts,
# so testing your models ensures you can not just change model without consequences


def test_input_model():
    with pytest.raises(ValueError):
        InputModel()


def test_filters():
    with pytest.raises(ValueError):
        Filters(data_type=-1)


def test_input_model_required_attrs_set():
    test_data = InputModel(
        name="Pero",
        data_type=DataTypeEnum.ULTRA_SUPRA_COOL,
        count=DataCounterLimits.MIN,
    )
    assert test_data.name == "Pero"
    assert test_data.data_type == DataTypeEnum.ULTRA_SUPRA_COOL
    assert test_data.count == DataCounterLimits.MIN
