import enum
import random
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

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
    first_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50,
        pattern=r"^[А-Яа-яЁё\s]+$",
        description="First name of the person",
        examples=["Иван"],
    )
    father_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50,
        pattern=r"^[А-Яа-яЁё\s]+$",
        description="Father's name of the person",
        examples=["Иванов"],
    )
    last_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50,
        pattern=r"^[А-Яа-яЁё\s]+$",
        description="Last name of the person",
        examples=["Иванович"],
    )
    birth_date: Optional[datetime] = Field(
        datetime.now().replace(year=datetime.now().year - 18)
    )
    birth_place: Optional[str] = Field(max_length=500)
    gender: Optional[Gender] = Gender.m.name
    phone: int = Field(random.randint(10000000000, 99999999999))
    email: EmailStr
    ip: Optional[str] = Field(default="127.0.0.1")

    @field_validator("birth_date", mode="before")
    def validate_birth_date(cls, v: str):
        if not v:
            return v
        v_datetime = datetime.fromisoformat(str(v)).replace(tzinfo=None)
        today = datetime.now()
        min_date = today.replace(year=today.year - 100)
        max_date = today.replace(year=today.year - 18)
        if not (min_date <= v_datetime <= max_date):
            raise ValueError("Birth date must be between 18 and 100 years ago.")
        return v

    @field_validator("phone", mode="before")
    def validate_phone(cls, v: int):
        phone_str = int(v).__str__()
        if len(phone_str) != 11:
            raise ValueError("Phone number must be exactly 11 digits long.")
        return int(v)


class Consent(BaseModel):
    status: Optional[bool]
    datetime: Optional[datetime]


class MailingConsent(Consent):
    pass


class Codes(BaseModel):
    snils: Optional[str] = Field(max_length=12)
    inn: Optional[str] = Field(max_length=12)


class Passport(BaseModel):
    seria: Optional[int] = Field(random.randint(1000, 9999))
    number: Optional[int] = Field(random.randint(100000, 999999))
    issuer: Optional[str] = Field(max_length=255)
    issuer_code: Optional[str] = Field(max_length=20)
    date: Optional[datetime]

    @field_validator("seria", mode="before")
    def validate_seria(cls, v: int):
        if not v:
            return v
        seria_str = str(v)
        if len(seria_str) != 4:
            raise ValueError("Passport seria must be exactly 4 digits long.")
        return v

    @field_validator("number", mode="before")
    def validate_number(cls, v: int):
        if not v:
            return v
        number_str = str(v)
        if len(number_str) != 6:
            raise ValueError("Passport number must be exactly 6 digits long.")
        return v


class Credit(BaseModel):
    amount: Optional[Decimal] = Field(1, gt=0)
    term: Optional[int] = Field(1, gt=0)


class Income(BaseModel):
    salary: Optional[Decimal] = Field(1, gt=0)


class Address(BaseModel):
    address: Optional[str] = Field(max_length=500, default=None)
    country: Optional[str] = Field(max_length=60, default=None)
    country_iso: Optional[str] = Field(min_length=2, max_length=2, default=None)
    postal_code: Optional[str] = Field(max_length=6, default=None)

    region: Optional[str] = Field(max_length=60, default=None)
    region_type: Optional[str] = Field(max_length=20, default=None)
    region_fias_id: Optional[str] = Field(max_length=36, default=None)
    region_kladr_code: Optional[int] = Field(ge=13, le=13, default=None)

    region_area: Optional[str] = Field(max_length=60, default=None)
    region_area_type: Optional[str] = Field(max_length=20, default=None)
    region_area_fias_id: Optional[str] = Field(max_length=36, default=None)
    region_area_kladr_code: Optional[int] = Field(ge=13, le=13, default=None)

    city: Optional[str] = Field(max_length=60, default=None)
    city_type: Optional[str] = Field(max_length=20, default=None)
    city_fias_id: Optional[str] = Field(max_length=36, default=None)
    city_kladr_code: Optional[int] = Field(ge=13, le=13, default=None)

    city_district: Optional[str] = Field(max_length=60, default=None)
    city_district_fias_id: Optional[str] = Field(max_length=36, default=None)
    city_district_type: Optional[str] = Field(max_length=20, default=None)
    city_district_kladr_code: Optional[int] = Field(ge=13, le=13, default=None)

    settlement: Optional[str] = Field(max_length=60, default=None)
    settlement_type: Optional[str] = Field(max_length=20, default=None)
    settlement_fias_id: Optional[str] = Field(max_length=36, default=None)
    settlement_kladr_code: Optional[int] = Field(ge=13, le=13, default=None)

    street: Optional[str] = Field(max_length=60, default=None)
    street_type: Optional[str] = Field(max_length=20, default=None)
    street_fias_id: Optional[str] = Field(max_length=36, default=None)
    street_kladr_code: Optional[int] = Field(ge=13, le=13, default=None)

    house: Optional[str] = Field(max_length=60, default=None)
    house_type: Optional[str] = Field(max_length=20, default=None)

    block: Optional[str] = Field(max_length=60, default=None)
    block_type: Optional[str] = Field(max_length=20, default=None)

    flat_num: Optional[str] = Field(max_length=60, default=None)
    flat_type: Optional[str] = Field(max_length=20, default=None)


class AddrReg(Address):
    pass


class AddrFact(Address):
    equal_to_reg: Optional[bool]


class Meta(BaseModel):
    is_test: Optional[bool] = True
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


class AcceptLeadBase(BaseModel):
    type: Literal["lead"] = Field("lead")
    api_token: str
    product: int = Field(ge=1, le=2)
    stream: str = Field(min_length=2, max_length=64, pattern=alphanumeric_pattern)


class AcceptLeadAttributes(BaseModel):
    sales: List[Sales] = []
    meta: Meta
    user: User
    consent: Consent
    mailing_consent: MailingConsent
    codes: Codes
    passport: Passport
    credit: Credit
    income: Income
    addr_reg: AddrReg
    addr_fact: AddrFact


class AcceptLeadCreate(AcceptLeadBase, AcceptLeadAttributes):
    pass


class AcceptLead(AcceptLeadBase, AcceptLeadAttributes):
    id: Optional[int] = None
    applied_at: datetime
