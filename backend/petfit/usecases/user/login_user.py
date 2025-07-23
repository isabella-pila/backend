from petfit.domain.value_objects.email_vo import Email
from petfit.domain.value_objects.password import Password
from petfit.domain.entities.user import User
from petfit.domain.repositories.user_repository import UserRepository
from typing import Optional

class LoginUserUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def execute(self, email: Email, plain_password: str) -> Optional[User]:
        user = await self.repository.login(email) 

        if not user:
            return None  # Usuário não encontrado

        if user.password.verify(plain_password):
            return user
        
        return None  # Credenciais inválidas (senha incorreta)