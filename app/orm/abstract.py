import typing
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

from sqlmodel import SQLModel

T = TypeVar("T", bound=SQLModel)


class GenericRepository(Generic[T], ABC):

    @abstractmethod
    def get_by_id(self, id: typing.Any) -> Optional[T]:
        """Get a single record by id.

        Args:
            id (int): Record id.

        Returns:
            Optional[T]: Record or none.
        """
        raise NotImplementedError()

    @abstractmethod
    def list(self, **filters) -> List[T]:
        """Gets a list of records

        Args:
            **filters: Filter conditions, several criteria are linked with a logical 'and'.

         Raises:
            ValueError: Invalid filter condition.

        Returns:
            List[T]: List of records.
        """
        raise NotImplementedError()

    @abstractmethod
    def add(self, record: T) -> T:
        """Creates a new record.

        Args:
            record (T): The record to be created.

        Returns:
            T: The created record.
        """
        raise NotImplementedError()

    @abstractmethod
    def update(self, record: T) -> T:
        """Updates an existing record.

        Args:
            record (T): The record to be updated incl. record id.

        Returns:
            T: The updated record.
        """
        raise NotImplementedError()

    @abstractmethod
    def delete(self, id: typing.Any) -> None:
        """Deletes a record by id.

        Args:
            id (int): Record id.
        """
        raise NotImplementedError()
