from typing import List, Optional

import databases
from pydantic import PositiveInt, PostgresDsn
from simple_example.domain_logic.exceptions import ObjectNotFound
from simple_example.domain_logic.models import DataEntity, Filters, InputModel
from simple_example.domain_logic.repository import AbstractRepository
from sqlalchemy import (
    Column,
    Integer,
    String,
    Table,
    and_,
    create_engine,
    delete,
    exists,
    insert,
    select,
    update,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query

Base = declarative_base()
metadata = Base.metadata


EntityDataTable = Table(
    "data_model",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("data_type", Integer, nullable=False),
    Column("count", Integer, nullable=False),
)


def setup_db_connection(database_url: PostgresDsn):
    engine = create_engine(database_url)
    metadata.create_all(engine, checkfirst=True)

    return databases.Database(database_url)


class SQLRepository(AbstractRepository):
    def __init__(self, database: databases.Database):
        self.database = database

    async def execute_query_with_one_result(
        self, query: select
    ) -> Optional[DataEntity]:
        result = await self.database.fetch_one(query)
        if result:
            return DataEntity(**result)
        return None

    async def execute_query_with_many_results(
        self, query: select
    ) -> Optional[List[DataEntity]]:
        results = await self.database.fetch_all(query)
        if results:
            return [DataEntity(**result) for result in results]
        return []

    async def get(self, item_id: PositiveInt) -> Optional[DataEntity]:
        query = select([EntityDataTable]).where(EntityDataTable.c.id == item_id)
        return await self.execute_query_with_one_result(query)

    async def create(self, input_data: InputModel) -> DataEntity:
        insert_query = insert(EntityDataTable).values(**input_data.model_dump())
        last_record_id = await self.database.execute(insert_query)
        get_query = select([EntityDataTable]).where(
            EntityDataTable.c.id == last_record_id
        )
        return await self.execute_query_with_one_result(get_query)

    async def exists(self, input_data: InputModel) -> bool:
        get_query = EntityDataTable.select(
            and_(
                EntityDataTable.c.name == input_data.name,
                EntityDataTable.c.data_type == input_data.data_type,
                EntityDataTable.c.count == input_data.count,
            )
        )
        result = await self.database.fetch_val(select([exists(get_query)]).as_scalar())
        return result or 0

    async def update(self, item_id: PositiveInt, update_data: InputModel) -> DataEntity:
        query = (
            update(EntityDataTable)
            .returning(EntityDataTable.c.id)
            .where(EntityDataTable.c.id == item_id)
            .values(update_data.model_dump(exclude_unset=True))
        )
        result = await self.database.fetch_val(
            query.cte("updated_data").count().as_scalar()
        )
        if result:
            return await self.get(item_id=item_id)
        raise ObjectNotFound()

    async def delete(self, item_id: PositiveInt) -> bool:
        query = (
            delete(EntityDataTable)
            .returning(EntityDataTable.c.id)
            .where(EntityDataTable.c.id == item_id)
        )
        result = await self.database.fetch_val(
            query.cte("delete_data").count().as_scalar()
        )
        return result == 1

    @staticmethod
    def __filter_item(query: Query, filters: Filters) -> Query:
        if filters.search_string is not None:
            query = query.where(
                EntityDataTable.c.name.ilike(f"%{filters.search_string}%")
            )
        if filters.count_lower_limit is not None:
            query = query.where(EntityDataTable.c.count >= filters.count_lower_limit)
        if filters.count_upper_limit is not None:
            query = query.where(EntityDataTable.c.count <= filters.count_upper_limit)
        if filters.data_type is not None:
            query = query.where(EntityDataTable.c.data_type == filters.data_type)
        return query

    async def list(self, filters: Filters) -> List[Optional[DataEntity]]:
        query = self.__filter_item(query=select([EntityDataTable]), filters=filters)
        return await self.execute_query_with_many_results(query=query)
