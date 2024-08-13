from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed

from app.api.api import api_router
from app.loguru_logging import configure_logging
from app.settings import prisma


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup")
    await prisma.connect()
    yield
    await prisma.disconnect()
    logger.info("shutdown")


def create_fastapi_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        lifespan=lifespan,
    )
    app.include_router(api_router)
    return app
