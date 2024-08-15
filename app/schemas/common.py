import enum
from typing import Optional, Union, List

from prisma import types
from pydantic import BaseModel


class ResponseModel(BaseModel):
    status: int
    message: dict | str


class FileExtEnum(str, enum.Enum):
    xlsx = "xlsx"
    csv = "csv"
    json = "json"


class PrismaFilter(BaseModel):
    take: Optional[int] = None
    skip: Optional[int] = None
    where: Optional[types.LeadWhereInput] = None
    cursor: Optional[types.LeadWhereUniqueInput] = None
    include: Optional[types.LeadInclude] = None
    order: Optional[Union[dict, List[dict]]] = None
    distinct: Optional[List[types.LeadScalarFieldKeys]] = None
