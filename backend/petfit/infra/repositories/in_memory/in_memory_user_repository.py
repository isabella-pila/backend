import uuid
from petfit.domain.entities.user import User
from petfit.domain.value_objects.email_vo import Email
from petfit.domain.value_objects.password import Password
from typing import Optional
from petfit.domain.repositories.user_repository import UserRepository # Importação da interface

class InMemoryUserRepository(UserRepository): # Herda da interface
    def __init__(self):
        self._users = {}
        self._current_user_id = None

    # O retorno agora é 'User' para consistência com a interface
    def register(self, user: User) -> User:
        self._users[user.id] = user
        self._current_user_id = user.id
        return user

    # Os tipos de email/password e o retorno agora são consistentes com a interface
    def login(self, email: Email, password: Password) -> Optional[User]:
        for user in self._users.values():
            # Certifique-se de que a comparação de Email e Password funciona corretamente
            if user.email == email and user.password == password:
                self._current_user_id = user.id
                return user
        return None

    def user_logout(self) -> None: # Nome já corrigido anteriormente
        self._current_user_id = None

    def get_current_user(self) -> Optional[User]:
        if self._current_user_id is None:
            return None
        return self._users.get(self._current_user_id)

    def set_current_user(self, user: User) -> None:
        self._users[user.id] = user
        self._current_user_id = user.id

    # O retorno agora é 'Optional[User]' para consistência com a interface
    def update(self, user: User) -> Optional[User]:
        if user.id in self._users:
            self._users[user.id] = user
            return user
        return None    

    # get_by_id adicionado e consistente com a interface
    def get_by_id(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)