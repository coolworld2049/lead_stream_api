from abc import ABC
from typing import Any

from app import models
from app.orm.abstract import GenericRepository
from app.orm.sql.base import GenericSqlRepository


class UserReposityBase(GenericRepository[models.User], ABC):
    pass


class UserRepository(GenericSqlRepository[models.User], UserReposityBase):
    def __init__(self, session: Any) -> None:
        super().__init__(session, models.User)
