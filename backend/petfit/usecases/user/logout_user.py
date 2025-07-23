from petfit.domain.repositories.user_repository import UserRepository


class LogoutUserUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self) -> None:
        self.repository.user_logout()