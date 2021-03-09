from typing import List, Optional

from pydantic import PositiveInt

from simple_example.domain_logic.consts import CountLimit, DataTypeEnum
from simple_example.domain_logic.exceptions import DuplicateDataException
from simple_example.domain_logic.models import DataEntity, Filters, InputModel
from simple_example.domain_logic.repository import AbstractRepository


class DomainLogicManager:
    def __init__(self, repository: AbstractRepository):
        self.repository = repository

    async def list(self, filters: Filters) -> List[Optional[DataEntity]]:
        return await self.repository.list(filters=filters)

    async def get(self, item_id: PositiveInt) -> DataEntity:
        return await self.repository.get(item_id=item_id)

    async def create(self, input_data: InputModel) -> DataEntity:
        is_duplicate = await self.repository.exists(input_data=input_data)
        if is_duplicate:
            raise DuplicateDataException()
        return await self.repository.create(input_data=input_data)

    async def update(self, item_id: PositiveInt, update_data: InputModel) -> DataEntity:
        return await self.repository.update(item_id=item_id, update_data=update_data)

    async def delete(self, item_id: PositiveInt) -> bool:
        return await self.repository.delete(item_id=item_id)

    async def search_list(
        self,
        search_string: None,
        data_type: None,
        count_upper_limit: None,
        count_lower_limit: Optional[CountLimit] = None,
    ):
        return await self.repository.list(
            filters=Filters(
                search_string=search_string,
                data_type=data_type,
                count_lower_limit=count_lower_limit,
                count_upper_limit=count_upper_limit,
            )
        )
