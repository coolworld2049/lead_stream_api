from abc import ABC
from typing import Type, Optional, Any, Sequence

from sqlalchemy import Row, RowMapping, update, delete
from sqlmodel import Session
from sqlmodel.sql.expression import SelectOfScalar, select, and_

from app.orm.abstract import GenericRepository, T


class GenericSqlRepository(GenericRepository[T], ABC):
    def __init__(self, session: Session, model_cls: Type[T]) -> None:
        self._session = session
        self._model_cls = model_cls

    def _construct_get_stmt(self, id: int) -> SelectOfScalar:
        stmt = select(self._model_cls).where(self._model_cls.id == id)
        return stmt

    def get_by_id(self, id: int) -> Optional[T]:
        stmt = self._construct_get_stmt(id)
        return self._session.execute(stmt).scalar_one()

    def _construct_list_stmt(self, **filters) -> SelectOfScalar:
        stmt = select(self._model_cls)
        where_clauses = []
        for c, v in filters.items():
            if not hasattr(self._model_cls, c):
                raise ValueError(f"Invalid column name {c}")
            where_clauses.append(getattr(self._model_cls, c) == v)

        if len(where_clauses) == 1:
            stmt = stmt.where(where_clauses[0])
        elif len(where_clauses) > 1:
            stmt = stmt.where(and_(*where_clauses))
        return stmt

    def list(self, **filters) -> Sequence[Row[Any] | RowMapping | Any]:
        stmt = self._construct_list_stmt(**filters)
        return self._session.execute(stmt).scalars().all()

    def add(self, record: T) -> T:
        with self._session.begin():
            self._session.add(record)
            self._session.flush()
            self._session.refresh(record)
            return record

    def update(self, record: T) -> T:
        stmt = (
            update(self._model_cls)
            .values(**record.model_dump())
            .where(self._model_cls.id == record.id)
            .returning(self._model_cls)
        )
        with self._session.begin():
            result = self._session.execute(stmt)
            record = result.scalar_one()
            self._session.flush()
            return record

    def delete(self, id: int) -> None:
        stmt = (
            delete(self._model_cls)
            .where(self._model_cls.id == id)
            .returning(self._model_cls)
        )
        with self._session.begin():
            self._session.execute(stmt).scalar_one()
