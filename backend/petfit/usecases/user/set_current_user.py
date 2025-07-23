from petfit.domain.repositories.user_repository import UserRepository
from petfit.domain.entities.user import User


class SetCurrentUserUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, user: User) -> None:
        self.repository.set_current_user(user)