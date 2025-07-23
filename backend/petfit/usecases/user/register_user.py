from petfit.domain.entities.user import User
from petfit.domain.repositories.user_repository import UserRepository
from typing import Optional


class RegisterUserUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def execute(self, user: User) -> Optional[User]:
        existing_user = await self.repository.get_by_email(user.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        return await self.repository.register(user)