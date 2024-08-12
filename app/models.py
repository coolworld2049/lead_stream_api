from sqlmodel import Field, SQLModel


# ------------- User -------------


class UserBase(SQLModel):
    username: str = Field(nullable=False, unique=True, index=True)


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class User(UserBase, table=True):
    __tablename__ = "users"
    id: int | None = Field(primary_key=True, default=None)
