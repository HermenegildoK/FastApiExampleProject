from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import ValidationError

from simple_example.domain_logic.exceptions import (
    DuplicateDataException,
    ObjectNotFound,
)
from simple_example.web_app_example.db_initialize import set_database
from simple_example.web_app_example.endpoints import main_router
from simple_example.web_app_example.settings import Settings, get_settings


def app_setup(settings: Optional[Settings] = None):
    settings = get_settings() if settings is None else settings
    app = FastAPI()

    @app.exception_handler(DuplicateDataException)
    async def duplicate_exception_handler(
        request: Request, exc: DuplicateDataException
    ):
        return JSONResponse(status_code=400, content={"message": f"{exc.message}"})

    @app.exception_handler(ObjectNotFound)
    async def not_found_exception_handler(request: Request, exc: ObjectNotFound):
        return JSONResponse(status_code=400, content={"message": f"{exc.message}"})

    @app.exception_handler(ValidationError)
    async def not_found_exception_handler(request: Request, exc: ValidationError):
        return JSONResponse(status_code=400, content={"detail": exc.errors()})

    app.include_router(main_router, prefix=settings.API_PREFIX)
    set_database(settings)
    from simple_example.web_app_example.db_initialize import database  #noqa

    @app.on_event("startup")
    async def startup():
        await database.connect()

    @app.on_event("shutdown")
    async def shutdown():
        await database.disconnect()

    @app.get("/")
    async def root():
        return RedirectResponse("/docs")

    return app
