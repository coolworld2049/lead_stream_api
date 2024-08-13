from prisma.partials import (
    SaleCreateWithoutRelationsInput,
    MetaCreateWithoutRelationsInput,
    UserCreateWithoutRelationsInput,
    AddressCreateWithoutRelationsInput,
)
from pydantic import BaseModel
from typing_extensions import List


class PrismaErrorResponse(BaseModel):
    type: str = "PrismaError"
    message: str
    details: dict


class MetaCreateNestedWithoutRelationsInput(BaseModel):
    create: "MetaCreateWithoutRelationsInput"


class SaleCreateManyNestedWithoutRelationsInput(BaseModel):
    create: List["SaleCreateWithoutRelationsInput"]


class UserCreateNestedWithoutRelationsInput(BaseModel):
    create: "UserCreateWithoutRelationsInput"


class AddressCreateNestedWithoutRelationsInput(BaseModel):
    create: "AddressCreateWithoutRelationsInput"


class LeadCreateInputOptional(BaseModel):
    meta: "MetaCreateNestedWithoutRelationsInput"
    sales: "SaleCreateManyNestedWithoutRelationsInput"
    user: "UserCreateNestedWithoutRelationsInput"
    addressReg: "AddressCreateNestedWithoutRelationsInput"
    addressFact: "AddressCreateNestedWithoutRelationsInput"


class LeadCreateInput(LeadCreateInputOptional):
    type: str
    apiToken: str
    product: int
    stream: str
