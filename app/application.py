from contextlib import asynccontextmanager

import prisma
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from loguru import logger
from starlette import status
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse
from tenacity import retry, stop_after_attempt, wait_fixed

from app.api.api import api_router
from app.loguru_logging import configure_logging
from app.middleware import PrismaErrorMiddleware
from app.settings import prisma as _prisma, settings


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup")
    prisma.register(_prisma)
    await _prisma.connect()
    yield
    await _prisma.disconnect()
    logger.info("shutdown")


def create_fastapi_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=f"/api/{settings.SECURE_PATH}/openapi.json"
    )
    app.add_middleware(PrismaErrorMiddleware)
    app.include_router(api_router)

    def check_secure_path(secure_path: str):
        if secure_path != settings.SECURE_PATH:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Forbidden"
            )

    @app.get("/docs/{secure_path}", response_class=HTMLResponse, include_in_schema=False)
    async def get_docs(secure_path: str) -> HTMLResponse:
        check_secure_path(secure_path)
        return get_swagger_ui_html(openapi_url=f"/api/{secure_path}/openapi.json", title="docs")

    @app.get("/redoc/{secure_path}", response_class=HTMLResponse, include_in_schema=False)
    async def get_redoc(secure_path: str) -> HTMLResponse:
        check_secure_path(secure_path)
        return get_redoc_html(openapi_url=f"/api/{secure_path}/openapi.json", title="red")

    return app
