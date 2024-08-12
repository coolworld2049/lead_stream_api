from abc import ABC, abstractmethod
from typing import Callable

from sqlalchemy.orm.scoping import ScopedSession
from sqlmodel import Session

from app.repository.user import UserRepository, UserReposityBase


class IUnitOfWork(ABC):
    user_repository: UserReposityBase

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value:
            self.rollback()
        self.commit()

    @abstractmethod
    def commit(self):
        raise NotImplementedError()

    @abstractmethod
    def rollback(self):
        raise NotImplementedError()


class UnitOfWork(IUnitOfWork):
    def __init__(
        self,
        sql_session_factory: Callable[[], Session | ScopedSession],
    ) -> None:
        self._sql_session_factory: Session | ScopedSession = sql_session_factory

    def __enter__(self):
        self._session = self._sql_session_factory()
        self.user_repository = UserRepository(self._session)
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value:
            self.rollback()
        else:
            self.commit()
        self._session.close()

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()
