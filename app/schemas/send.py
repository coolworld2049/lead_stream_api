import random
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator


class SendLeadBase(BaseModel):
    phone: int = Field(random.randint(70000000000, 79999999999))
    campaign: str
    token: str

    @field_validator("phone", mode="before")
    def validate_phone(cls, v: int):
        phone_str = str(v)
        if len(phone_str) != 11:
            raise ValueError("Phone number must be exactly 11 digits long.")
        if not phone_str.startswith("7"):
            raise ValueError("Phone number must be start with 7")
        return v


class SendLeadOptional(BaseModel):
    external_id: Optional[str] = Field(...)
    sub1: Optional[str] = Field(..., min_length=2, max_length=128)
    first_name: Optional[str] = Field(
        ...,
        examples=["Иван"],
    )
    last_name: Optional[str] = Field(
        ...,
        examples=["Иванович"],
    )
    father_name: Optional[str] = Field(
        ...,
        examples=["Иванов"],
    )


class SendLeadCreate(SendLeadBase, SendLeadOptional):
    pass


class SendLead(SendLeadBase, SendLeadOptional):
    id: int | None = None


class UnicoreResponseHTTP401(BaseModel):
    error: str


class UnicoreResponseHTTP422(BaseModel):
    error: str
    status: str


class UnicoreResponseHTTP200(BaseModel):
    lead_id: int
    lead_status: Literal["approved", "cancelled"]
    status: str
