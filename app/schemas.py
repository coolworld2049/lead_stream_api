from pydantic import BaseModel


class PrismaErrorResponse(BaseModel):
    type: str = "PrismaError"
    message: str
    details: dict
