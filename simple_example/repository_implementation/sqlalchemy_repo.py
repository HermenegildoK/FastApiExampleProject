from typing import List, Optional

from pydantic import PositiveInt, PostgresDsn
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    and_,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Query

from simple_example.domain_logic.exceptions import ObjectNotFound
from simple_example.domain_logic.models import DataEntity, Filters, InputModel
from simple_example.domain_logic.repository import AbstractRepository

metadata = MetaData()


EntityDataTable = Table(
    "data_model",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("data_type", Integer, nullable=False),
    Column("count", Integer, nullable=False),
)


class Database:
    def __init__(self, engine):
        self.engine = engine

    async def connect(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    async def disconnect(self):
        await self.engine.dispose()


def setup_db_connection(database_url: PostgresDsn):
    # make sure to use string form to avoid sqlalchemy exception:
    # sqlalchemy.exc.ArgumentError: Expected string or URL object, got MultiHostUrl
    engine = create_async_engine(database_url.unicode_string())

    return Database(engine)


class SQLRepository(AbstractRepository):
    def __init__(self, database: Database):
        self.engine = database.engine

    async def execute_query_with_one_result(
        self, query: select
    ) -> Optional[DataEntity]:
        async with self.engine.connect() as conn:
            result = await conn.execute(query)
            db_data = result.first()
            if db_data:
                return DataEntity(**db_data._mapping)
            return None

    async def execute_query_with_many_results(
        self, query: select
    ) -> Optional[List[DataEntity]]:
        async with self.engine.connect() as conn:
            result = await conn.execute(query)
            results = result.all()
            if results:
                return [DataEntity(**result._mapping) for result in results]
        return []

    async def get(self, item_id: PositiveInt) -> Optional[DataEntity]:
        query = select(EntityDataTable).where(EntityDataTable.c.id == item_id)
        return await self.execute_query_with_one_result(query)

    async def create(self, input_data: InputModel) -> DataEntity:
        insert_query = (
            insert(EntityDataTable)
            .values(**input_data.model_dump())
            .returning(EntityDataTable.c.id)
        )
        async with self.engine.begin() as conn:
            last_record_id = await conn.execute(insert_query)
            last_record_id = last_record_id.scalar()
        get_query = select(EntityDataTable).where(
            EntityDataTable.c.id == last_record_id
        )
        new_object = await self.execute_query_with_one_result(get_query)
        if not new_object:
            raise ObjectNotFound()
        return new_object

    async def exists(self, input_data: InputModel) -> bool:
        exists_criteria = (
            select(EntityDataTable.c.id)
            .where(
                and_(
                    EntityDataTable.c.name == input_data.name,
                    EntityDataTable.c.data_type == input_data.data_type,
                    EntityDataTable.c.count == input_data.count,
                )
            )
            .exists()
        )
        stmt = select(EntityDataTable.c.id).where(exists_criteria)
        async with self.engine.begin() as conn:
            result = await conn.execute(stmt)
            return result.scalar() or 0

    async def update(self, item_id: PositiveInt, update_data: InputModel) -> DataEntity:
        query = (
            update(EntityDataTable)
            .returning(EntityDataTable.c.id)
            .where(EntityDataTable.c.id == item_id)
            .values(update_data.model_dump(exclude_unset=True))
        )
        async with self.engine.begin() as conn:
            result = await conn.execute(query)
            item_exists = result.scalar()
        if item_exists:
            return await self.get(item_id=item_id)
        raise ObjectNotFound()

    async def delete(self, item_id: PositiveInt) -> bool:
        query = (
            delete(EntityDataTable)
            .returning(EntityDataTable.c.id)
            .where(EntityDataTable.c.id == item_id)
        )
        async with self.engine.begin() as conn:
            result = await conn.execute(query)
            return result.scalar() == item_id

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
        query = self.__filter_item(query=select(EntityDataTable), filters=filters)
        return await self.execute_query_with_many_results(query=query)
