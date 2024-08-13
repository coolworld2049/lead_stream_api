from fastapi import Request
from prisma.errors import PrismaError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.schemas import PrismaErrorResponse


class PrismaErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except PrismaError as e:
            err = PrismaErrorResponse(
                type=e.__class__.__name__,
                message=str(e),
                details=self.get_error_details(e)
            )
            content = {
                "error": err.model_dump()
            }
            return JSONResponse(content=content, status_code=500)
        return response

    @staticmethod
    def get_error_details(error: PrismaError):
        return {
            "code": getattr(error, "code", "UnknownError"),
            "meta": getattr(error, "meta", None),
        }
