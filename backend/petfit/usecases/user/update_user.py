from petfit.domain.entities.user import User
from petfit.domain.repositories.user_repository import UserRepository
from typing import Optional


class UpdateUserUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, user: User) -> Optional[User]:
        return self.repository.update(user)