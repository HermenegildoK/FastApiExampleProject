from typing import List, Optional

from pydantic import PositiveInt

from simple_example.domain_logic.exceptions import ObjectNotFound
from simple_example.domain_logic.models import DataEntity, Filters, InputModel
from simple_example.domain_logic.repository import AbstractRepository


class Database:
    def __init__(self):
        self.storage = {}

    async def connect(self):
        self.storage = {}

    async def disconnect(self):
        self.storage = {}


class MemoryRepository(AbstractRepository):
    def __init__(self, database: Database):
        self.database = database

    async def get(self, item_id: PositiveInt) -> Optional[DataEntity]:
        return self.database.storage.get(item_id)

    async def create(self, input_data: InputModel) -> DataEntity:
        data_id = len(self.database.storage.keys()) + 1
        data = DataEntity(**input_data.dict(), id=data_id)
        self.database.storage[data_id] = data
        return data

    async def exists(self, input_data: InputModel) -> bool:
        for data_id in self.database.storage:
            if self.database.storage[data_id].dict(exclude={"id"}) == input_data.dict():
                return True
        return False

    async def update(self, item_id: PositiveInt, update_data: InputModel) -> DataEntity:
        data = await self.get(item_id=item_id)
        if data:
            new_data = update_data.dict(exclude_unset=True)
            for k in new_data:
                setattr(data, k, new_data[k])
            return data
        raise ObjectNotFound()

    async def delete(self, item_id: PositiveInt) -> bool:
        item = self.database.storage.pop(item_id, None)
        return item is not None

    @staticmethod
    def __filter_item(item: DataEntity, filters: Filters):
        if filters.search_string is not None:
            if item.name.find(filters.search_string) == -1:
                return False
        if filters.count_lower_limit is not None:
            if item.count < filters.count_lower_limit:
                return False
        if filters.count_upper_limit is not None:
            if item.count > filters.count_upper_limit:
                return False
        if filters.data_type is not None:
            if item.data_type != filters.data_type:
                return False
        return True

    async def list(self, filters: Filters) -> List[Optional[DataEntity]]:
        return [
            item
            for item in self.database.storage.values()
            if self.__filter_item(item, filters)
        ]
