from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import PositiveInt

from simple_example.domain_logic.manager import DomainLogicManager
from simple_example.domain_logic.models import DataEntity, Filters, InputModel
from simple_example.web_app_example.dependencies import get_manager, search_parameters

main_router = APIRouter()



@main_router.post("/search/")
async def search_data(
    filters: Filters, manager: DomainLogicManager = Depends(get_manager)
):
    return await manager.list(filters=filters)


@main_router.post("/data/", response_model=DataEntity)
async def create_data(
    data: InputModel, manager: DomainLogicManager = Depends(get_manager)
):
    return await manager.create(data)


@main_router.put("/data/{item_id}", response_model=DataEntity)
async def update_data(
    item_id: PositiveInt,
    data: InputModel,
    manager: DomainLogicManager = Depends(get_manager),
):
    return await manager.update(item_id=item_id, update_data=data)


@main_router.delete("/data/{item_id}")
async def delete_data(
    item_id: PositiveInt, manager: DomainLogicManager = Depends(get_manager)
):
    is_deleted = await manager.delete(item_id=item_id)
    return {"success": is_deleted}


@main_router.post("/filter/")
async def search_data(
    search_string: Optional[str] = None,
    data_type: Optional[int] = None,
    count_upper_limit: Optional[int] = None,
    count_lower_limit: Optional[int] = None,
    manager: DomainLogicManager = Depends(get_manager),
):
    return await manager.search_list(
        search_string=search_string,
        data_type=data_type,
        count_upper_limit=count_upper_limit,
        count_lower_limit=count_lower_limit,
    )

@main_router.get("/data/")
async def list_data(
    filters: Filters = Depends(search_parameters),
    manager: DomainLogicManager = Depends(get_manager),
):
    return await manager.list(filters=filters)
