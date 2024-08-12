from fastapi import FastAPI

from app.api.api import api_router
from app.lifespan import lifespan
from app.loguru_logging import configure_logging


def create_fastapi_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        lifespan=lifespan,
    )
    app.include_router(api_router)
    return app
