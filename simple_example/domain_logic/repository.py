from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import PositiveInt

from simple_example.domain_logic.models import DataEntity, Filters, InputModel


class AbstractRepository(ABC):
    @abstractmethod
    async def get(self, item_id: PositiveInt) -> Optional[DataEntity]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, input_data: InputModel) -> DataEntity:
        raise NotImplementedError

    @abstractmethod
    async def exists(self, input_data: InputModel) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def update(self, item_id: PositiveInt, update_data: InputModel) -> DataEntity:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, item_id: PositiveInt) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def list(self, filters: Filters) -> List[Optional[DataEntity]]:
        raise NotImplementedError
