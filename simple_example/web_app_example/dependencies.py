from typing import Optional

from fastapi import Depends

from simple_example.domain_logic.consts import DataTypeEnum
from simple_example.domain_logic.manager import DomainLogicManager
from simple_example.domain_logic.models import Filters
from simple_example.domain_logic.repository import AbstractRepository
from simple_example.repository_implementation.memory_repo import MemoryRepository
from simple_example.repository_implementation.sqlalchemy_repo import SQLRepository
from simple_example.web_app_example.settings import get_settings


def get_repository(settings=Depends(get_settings)):
    from simple_example.web_app_example.db_initialize import database  # noqa

    if settings.USE_DATABASE:

        def inner_get_repository() -> AbstractRepository:
            return SQLRepository(database=database)

    else:

        def inner_get_repository() -> AbstractRepository:
            return MemoryRepository(database)

    return inner_get_repository()


def get_manager(repository=Depends(get_repository)) -> DomainLogicManager:
    return DomainLogicManager(repository=repository)


async def search_parameters(
    q: Optional[str] = None, data_type: Optional[DataTypeEnum] = None
) -> Filters:
    return Filters(search_string=q, data_type=data_type)
