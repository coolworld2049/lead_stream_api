import enum
import random
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Union

import pytz
from prisma import types
from pydantic import BaseModel, EmailStr, Field
from pydantic import field_validator
from typing_extensions import Literal

# Define patterns for validation
ipv4_pattern = r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
ipv6_pattern = r"^([0-9a-fA-F]{1,4}:){7}([0-9a-fA-F]{1,4}|:)$"
alphanumeric_pattern = r"^[A-Za-z0-9]+$"


class Gender(str, enum.Enum):
    f = "f"
    m = "m"


class User(BaseModel):
    first_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        pattern=r"^[А-Яа-яЁё\s]+$",
        description="First name of the person",
        examples=["Иван"],
    )
    father_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        pattern=r"^[А-Яа-яЁё\s]+$",
        description="Father's name of the person",
        examples=["Иванов"],
    )
    last_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        pattern=r"^[А-Яа-яЁё\s]+$",
        description="Last name of the person",
        examples=["Иванович"],
    )
    birth_date: datetime = datetime.now().replace(year=datetime.now().year - 18)
    birth_place: str = Field(max_length=500)
    gender: Gender = Gender.m.name
    phone: int = Field(random.randint(10000000000, 99999999999))
    email: EmailStr
    ip: str = Field(default="127.0.0.1")

    @field_validator("birth_date", mode="before")
    def validate_birth_date(cls, v: str):
        v_datetime = datetime.fromisoformat(str(v))
        today = datetime.now()
        min_date = today.replace(year=today.year - 100)
        max_date = today.replace(year=today.year - 18)
        if not (min_date <= v_datetime <= max_date):
            raise ValueError("Birth date must be between 18 and 100 years ago.")
        return v

    @field_validator("phone", mode="before")
    def validate_phone(cls, v: int):
        phone_str = str(v)
        if len(phone_str) != 11:
            raise ValueError("Phone number must be exactly 11 digits long.")
        return v


class Consent(BaseModel):
    status: bool
    datetime: datetime


class Codes(BaseModel):
    snils: str = Field(max_length=12)
    inn: str = Field(max_length=12)


class Passport(BaseModel):
    seria: int = Field(random.randint(1000, 9999))
    number: int = Field(random.randint(100000, 999999))
    issuer: str = Field(max_length=255)
    issuer_code: str = Field(max_length=20)
    date: datetime

    @field_validator("seria", mode="before")
    def validate_seria(cls, v: int):
        seria_str = str(v)
        if len(seria_str) != 4:
            raise ValueError("Passport seria must be exactly 4 digits long.")
        return v

    @field_validator("number", mode="before")
    def validate_number(cls, v: int):
        number_str = str(v)
        if len(number_str) != 6:
            raise ValueError("Passport number must be exactly 6 digits long.")
        return v


class Credit(BaseModel):
    amount: Decimal = Field(gt=0)
    term: int = Field(gt=0)


class Income(BaseModel):
    salary: Decimal = Field(gt=0)


class Address(BaseModel):
    address: Optional[str] = Field(max_length=500)
    country: str = Field(max_length=60)
    country_iso: str = Field(min_length=2, max_length=2)
    postal_code: str = Field(max_length=6)

    region: str = Field(max_length=60, default=None)
    region_type: str = Field(max_length=20, default=None)
    region_fias_id: str = Field(max_length=36, default=None)
    region_kladr_code: int = Field(ge=13, le=13, default=None)

    region_area: Optional[str] = Field(max_length=60, default=None)
    region_area_type: Optional[str] = Field(max_length=20, default=None)
    region_area_fias_id: Optional[str] = Field(max_length=36, default=None)
    region_area_kladr_code: Optional[int] = Field(ge=13, le=13, default=None)

    city: str = Field(max_length=60, default=None)
    city_type: str = Field(max_length=20, default=None)
    city_fias_id: str = Field(max_length=36, default=None)
    city_kladr_code: int = Field(ge=13, le=13, default=None)

    city_district: Optional[str] = Field(max_length=60, default=None)
    city_district_fias_id: Optional[str] = Field(max_length=36, default=None)
    city_district_type: Optional[str] = Field(max_length=20, default=None)
    city_district_kladr_code: Optional[int] = Field(ge=13, le=13, default=None)

    settlement: str = Field(max_length=60, default=None)
    settlement_type: str = Field(max_length=20, default=None)
    settlement_fias_id: str = Field(max_length=36, default=None)
    settlement_kladr_code: int = Field(ge=13, le=13, default=None)

    street: str = Field(max_length=60, default=None)
    street_type: str = Field(max_length=20, default=None)
    street_fias_id: str = Field(max_length=36, default=None)
    street_kladr_code: int = Field(ge=13, le=13, default=None)

    house: str = Field(max_length=60, default=None)
    house_type: str = Field(max_length=20, default=None)

    block: Optional[str] = Field(max_length=60, default=None)
    block_type: Optional[str] = Field(max_length=20, default=None)

    flat_num: Optional[str] = Field(max_length=60, default=None)
    flat_type: Optional[str] = Field(max_length=20, default=None)


class AddrReg(Address):
    pass


class AddrFact(Address):
    equal_to_reg: bool


class Meta(BaseModel):
    is_test: bool = True
    sub1: Optional[str] = Field(
        None, min_length=2, max_length=64, pattern=alphanumeric_pattern
    )
    sub2: Optional[str] = Field(
        None, min_length=2, max_length=64, pattern=alphanumeric_pattern
    )
    sub3: Optional[str] = Field(
        None, min_length=2, max_length=64, pattern=alphanumeric_pattern
    )
    sub4: Optional[str] = Field(
        None, min_length=2, max_length=64, pattern=alphanumeric_pattern
    )
    sub5: Optional[str] = Field(
        None, min_length=2, max_length=64, pattern=alphanumeric_pattern
    )


class Sales(BaseModel):
    campaignID: str


class LeadBase(BaseModel):
    type: Literal["lead"] = Field("lead")
    api_token: str
    product: int = Field(ge=1, le=2)
    applied_at: Optional[datetime] = datetime.now(tz=pytz.UTC)
    stream: str = Field(min_length=2, max_length=64, pattern=alphanumeric_pattern)


class LeadAttributes(BaseModel):
    sales: List[Sales]
    meta: Meta
    user: User
    consent: Consent
    mailing_consent: Consent
    codes: Codes
    passport: Passport
    credit: Credit
    income: Income
    addr_reg: AddrReg
    addr_fact: AddrFact


class Lead(LeadBase, LeadAttributes):
    pass


class PrismaFilter(BaseModel):
    take: Optional[int] = None
    skip: Optional[int] = None
    where: Optional[types.LeadWhereInput] = None
    cursor: Optional[types.LeadWhereUniqueInput] = None
    include: Optional[types.LeadInclude] = None
    order: Optional[Union[dict, List[dict]]] = None
    distinct: Optional[List[types.LeadScalarFieldKeys]] = None


class ErrorModel(BaseModel):
    error: str
    details: dict


class PrismaErrorModel(ErrorModel):
    type: str
    message: str


class ResponseModel(BaseModel):
    status: int
    message: dict


class FileExtEnum(str, enum.Enum):
    xlsx = "xlsx"
    csv = "csv"
    json = "json"


class LeadCreateResponseCampaign(BaseModel):
    campaignID: str
    status: str


class LeadCreateResponse(BaseModel):
    id: int
    status: str
    details: list[LeadCreateResponseCampaign]
