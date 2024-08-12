from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed

from app.orm.sql.session import sql_session_factory, on_database_startup, on_database_shutdown


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup")
    on_database_startup()
    try:
        app.state.sql_session_factory = sql_session_factory  # noqa
    except Exception as e:
        logger.error(e)

    yield
    on_database_shutdown()
    logger.info("shutdown")
