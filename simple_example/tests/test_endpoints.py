import pytest
import simple_example
from fastapi.testclient import TestClient
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
from simple_example.web_app_example.main import app_setup
from simple_example.web_app_example.settings import Settings, get_settings


def get_settings_override():
    return Settings(API_PREFIX="/test", USE_DATABASE=False)


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
    assert response.json() == [one_item.dict()]


def test_create_data(client, one_item):
    input_data = InputModel(
        name="Pero",
        data_type=DataTypeEnum.ULTRA_SUPRA_COOL,
        count=CountLimit(DataCounterLimits.MIN),
    ).dict()
    response = client.post("/test/data/", json=input_data)
    assert response.status_code == 200
    input_data.update(id=2)
    assert response.json() == input_data


def test_search_data(client, one_item):
    response = client.post("/test/search/", json={"q": "Pero"})
    assert response.status_code == 200
    assert response.json() == [one_item.dict()]


def test_update_data(client, one_item):
    input_data = InputModel(
        name="Pero",
        data_type=DataTypeEnum.SIMPLE,
        count=CountLimit(DataCounterLimits.MIN),
    ).dict()
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
    ).dict()
    input_data.update(count=DataCounterLimits.MAX * 2)
    response = client.put(f"/test/data/{one_item.id}", json=input_data)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {"limit_value": 99},
                "loc": ["body", "count"],
                "msg": "ensure this value is less than or equal to 99",
                "type": "value_error.number.not_le",
            }
        ]
    }
