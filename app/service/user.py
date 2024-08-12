from typing import List

from app import models
from app.repository.user import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def create_user(self, user: models.UserCreate) -> models.User:
        user_in = models.User(**user.model_dump(exclude_unset=True))
        result = self.repository.add(user_in)
        return result

    def get_user(self, id: int) -> models.User:
        result = self.repository.get_by_id(id)
        return result

    def get_users_list(self) -> List[models.User]:
        result = self.repository.list()
        return result

    def update_user(self, id: int, user: models.UserUpdate) -> models.User:
        user_in = models.User(**user.model_dump(exclude_unset=True))
        user_in.id = id
        result = self.repository.update(user_in)
        return result

    def delete_user(self, id: int) -> None:
        self.repository.delete(id)
