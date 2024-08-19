from fastapi import Request
from loguru import logger
from prisma.errors import PrismaError
from pydantic_core import ValidationError
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class PrismaErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except PrismaError as e:
            err = dict(
                type=e.__class__.__name__,
                message=str(e),
                detail=self.get_error_details(e),
            )
            logger.exception(e)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=err,
            )
        except ValidationError as ve:
            logger.exception(ve)
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=ve.json(indent=2, include_url=False),
            )
        except Exception as e:
            err = dict(
                type=e.__class__.__name__,
                message=str(e),
                detail="\n".join([str(x) for x in e.args]),
            )
            logger.exception(e)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=err,
            )
        return response

    @staticmethod
    def get_error_details(error: PrismaError):
        return {
            "code": getattr(error, "code", "UnknownError"),
            "meta": getattr(error, "meta", None),
        }
