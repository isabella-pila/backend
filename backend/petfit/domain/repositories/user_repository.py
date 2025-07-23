from abc import ABC, abstractmethod
from petfit.domain.entities.user import User
from petfit.domain.value_objects.email_vo import Email      # ADICIONADO: para tipagem correta no login
from petfit.domain.value_objects.password import Password  # ADICIONADO: para tipagem correta no login
from typing import Optional


class UserRepository(ABC):
    @abstractmethod
    # Retorno Optional[User] e tipos Email/Password para consistência com InMemory
    def login(self, email: Email, password: Password) -> Optional[User]:
        pass

    @abstractmethod
    # Retorno User para consistência com InMemory
    def register(self, user: User) -> User:
        pass

    @abstractmethod
    def get_current_user(self) -> Optional[User]:
        pass

    @abstractmethod
    def set_current_user(self, user: User) -> None:
        pass

    @abstractmethod
    def user_logout(self) -> None:
        pass

    @abstractmethod
    # Retorno Optional[User] para consistência com InMemory
    def update(self, user: User) -> Optional[User]:
        pass


    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[User]: ...

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[User]: ...