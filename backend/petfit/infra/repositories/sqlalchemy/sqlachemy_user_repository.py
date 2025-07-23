from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from petfit.domain.entities.user import User
from petfit.domain.repositories.user_repository import UserRepository
from petfit.domain.value_objects.email_vo import Email
from petfit.domain.value_objects.password import Password
from petfit.infra.models.user_model import UserModel

from petfit.infra.database import async_session


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._current_user: Optional[User] = None

    async def register(self, user: User) -> User:
        model = UserModel.from_entity(user)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        user.id = model.id
        return model.to_entity()

    async def login(self, email: Email) -> Optional[User]: # Remova o argumento 'password' aqui
            stmt = select(UserModel).where(UserModel.email == str(email))
            result = await self._session.execute(stmt)
            user_model = result.scalar_one_or_none()

            # Retorna a entidade User para o UseCase verificar a senha
            return user_model.to_entity() if user_model else None

    async def get_current_user(self) -> Optional[User]:
        if self._current_user is None:
            raise ValueError("Current user is not set. Please log in first.")
        stmt = select(UserModel).where(UserModel.id == str(self._current_user.id))
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            self._current_user = user.to_entity()
        else:
            self._current_user = None
        return self._current_user

    async def set_current_user(self, user: User) -> None:
        self._current_user = user

    async def user_logout(self) -> None:
        self._current_user = None

    async def get_by_email(self, email: Email) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == str(email))
        result = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return user_model.to_entity() if user_model else None

    async def get_by_id(self, id: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == str(id))
        result = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return user_model.to_entity() if user_model else None
    
    async def update(self, user):
        return super().update(user)
    
    