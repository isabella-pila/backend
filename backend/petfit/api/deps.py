# petfit/api/deps.py

# Instâncias SQLAlchemy
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials # <-- ADICIONADO HTTPBearer e HTTPAuthorizationCredentials
from jose import JWTError, jwt
from petfit.api.settings import settings
from petfit.domain.repositories.user_repository import UserRepository
from petfit.infra.repositories.sqlalchemy.sqlachemy_user_repository import (
    SQLAlchemyUserRepository,
)
from petfit.infra.repositories.sqlalchemy.sqlalchemy_recipe_repository import (
    SQLAlchemyRecipeRepository,
)

from sqlalchemy.ext.asyncio import AsyncSession
from petfit.infra.database import async_session
from petfit.domain.entities.user import User
from collections.abc import AsyncGenerator


# Dependência para obter a sessão do banco de dados
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


# Dependência para obter a instância do repositório de usuários
async def get_user_repository(
    db: AsyncSession = Depends(get_db_session),
) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(db)


# Dependência para obter a instância do repositório de receitas
async def get_recipe_repository( 
    db: AsyncSession = Depends(get_db_session),
) -> SQLAlchemyRecipeRepository:
    return SQLAlchemyRecipeRepository(db)


# Esquemas de segurança
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")
security_bearer = HTTPBearer() # <-- DEFINIÇÃO CENTRALIZADA AQUI


# Dependência para obter o usuário atualmente autenticado
async def get_current_user(
    # Use security_bearer para obter as credenciais brutas do cabeçalho
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer), # <-- Mude aqui para usar security_bearer
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    print(f"DEBUG: get_current_user - Iniciando. Token recebido: {credentials.credentials[:15]}...") # Use credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodifica o token JWT (credentials.credentials contém o token puro)
        payload = jwt.decode(
            credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        print(f"DEBUG: get_current_user - Payload decodificado: {payload}")
        
        # Extrai o ID do usuário (sub) do payload
        user_id: str = str(payload.get("sub"))
        if not user_id:
            print("DEBUG: get_current_user - user_id is None or empty. Raising credentials_exception.")
            raise credentials_exception

        # Busca o usuário no banco de dados usando o ID do token
        user = await user_repo.get_by_id(user_id)
        if user is None:
            print(f"DEBUG: get_current_user - User not found in DB for ID: {user_id}. Raising credentials_exception.")
            raise credentials_exception
        
        print(f"DEBUG: get_current_user - User successfully resolved: {user.id}")
        return user 

    except JWTError as e:
        print(f"DEBUG: get_current_user - JWTError detected: {e}. Raising credentials_exception.")
        raise credentials_exception
    except Exception as e:
        print(f"DEBUG: get_current_user - UNEXPECTED EXCEPTION (not JWTError): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during authentication."
        )