import os.path

import pytest
from fastapi.testclient import TestClient

import simple_example
from simple_example.domain_logic.consts import (
    CountLimit,
    DataCounterLimits,
    DataTypeEnum,
)
from simple_example.domain_logic.manager import DomainLogicManager
from simple_example.domain_logic.models import DataEntity, InputModel
from simple_example.repository_implementation.memory_repo import (
    Database,
    MemoryRepository,
)
from simple_example.web_app_example.application_factory import app_setup
from simple_example.web_app_example.settings import (
    LoggingConfiguration,
    Settings,
    get_settings,
)


def get_settings_override():
    return Settings(
        API_PREFIX="/test",
        USE_DATABASE=False,
        LOGGING=LoggingConfiguration(
            LOG_TO_FILE=True,
            LOG_JSON=True,
            JSON_LOG_FILE="test.json",
            LOG_TO_LEVEL_FILES=True,
            LOG_PATH=f"{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../test_logs'))}",
        ),
    )


@pytest.fixture(scope="function")
def one_item():
    return DataEntity(
        id=1,
        name="Pero",
        data_type=DataTypeEnum.ULTRA_SUPRA_COOL,
        count=CountLimit(DataCounterLimits.MAX),
    )


@pytest.fixture(scope="function")
def get_manager(one_item):
    database = Database()
    database.storage[one_item.id] = one_item
    return DomainLogicManager(repository=MemoryRepository(database=database))


@pytest.fixture(scope="function")
def client(get_manager):
    app = app_setup(settings=get_settings_override())
    app.dependency_overrides[get_settings] = get_settings_override
    app.dependency_overrides[
        simple_example.web_app_example.dependencies.get_manager
    ] = lambda: get_manager

    client = TestClient(app)
    return client


def test_list_data(client, one_item):
    response = client.get("/test/data/")
    assert response.status_code == 200
    assert response.json() == [one_item.model_dump()]


def test_create_data(client, one_item):
    input_data = InputModel(
        name="Pero",
        data_type=DataTypeEnum.ULTRA_SUPRA_COOL,
        count=CountLimit(DataCounterLimits.MIN),
    ).model_dump()
    response = client.post("/test/data/", json=input_data)
    assert response.status_code == 200
    input_data.update(id=2)
    assert response.json() == input_data


def test_search_data(client, one_item):
    response = client.post("/test/search/", json={"q": "Pero"})
    assert response.status_code == 200
    assert response.json() == [one_item.model_dump()]


def test_update_data(client, one_item):
    input_data = InputModel(
        name="Pero",
        data_type=DataTypeEnum.SIMPLE,
        count=CountLimit(DataCounterLimits.MIN),
    ).model_dump()
    response = client.put(f"/test/data/{one_item.id}", json=input_data)
    assert response.status_code == 200
    input_data.update(id=one_item.id)
    assert response.json() == input_data


def test_delete_data(client, one_item):
    response = client.delete(f"/test/data/{one_item.id}")
    assert response.status_code == 200
    assert response.json() == {"success": True}


def test_update_data_fail(client, one_item):
    input_data = InputModel(
        name="Pero",
        data_type=DataTypeEnum.SIMPLE,
        count=CountLimit(DataCounterLimits.MAX),
    ).model_dump()
    input_data.update(count=DataCounterLimits.MAX * 2)
    response = client.put(f"/test/data/{one_item.id}", json=input_data)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {"le": 99},
                "input": 198,
                "loc": ["body", "count"],
                "msg": "Input should be less than or equal to 99",
                "type": "less_than_equal",
                "url": "https://errors.pydantic.dev/2.1/v/less_than_equal",
            }
        ]
    }
