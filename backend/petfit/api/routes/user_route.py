# petfit/api/routes/user_route.py

from fastapi import APIRouter, HTTPException, Depends, status 
from petfit.usecases.user.register_user import RegisterUserUseCase
from petfit.usecases.user.login_user import LoginUserUseCase
from petfit.usecases.user.logout_user import LogoutUserUseCase
from petfit.usecases.user.get_current_user import GetCurrentUserUseCase
from petfit.domain.entities.user import User
from petfit.domain.value_objects.email_vo import Email
from petfit.domain.value_objects.password import Password, PasswordValidationError
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
# Importe HTTPAuthorizationCredentials e security_bearer do deps.py
from fastapi.security import HTTPAuthorizationCredentials # <-- ADICIONADO
from petfit.api.deps import get_db_session, get_user_repository, get_current_user, security_bearer # <-- ADICIONADO security_bearer
from petfit.infra.repositories.sqlalchemy.sqlachemy_user_repository import (
    SQLAlchemyUserRepository,
)
# REMOVER ESTAS LINHAS: from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# REMOVER ESTA LINHA: security = HTTPBearer() # A instância agora está em deps.py

from petfit.api.schemas.user_schema import (
    RegisterUserInput,
    UserOutput,
    TokenResponse,
)
from petfit.api.schemas.message_schema import MessageOutput
from petfit.api.security import create_access_token
from petfit.domain.repositories.user_repository import UserRepository
from petfit.api.schemas.user_schema import LoginUserInput
from petfit.api.security import verify_token


router = APIRouter()

# ----------------------
# Register
# ----------------------


@router.post(
    "/register",
    response_model=MessageOutput,
    summary="Registrar novo usuário",
    description="Cria um novo usuário com nome, email e senha forte.",
    status_code=status.HTTP_201_CREATED 
)
async def register_user(
    data: RegisterUserInput, db: AsyncSession = Depends(get_db_session)
):
    try:
        user_repo = SQLAlchemyUserRepository(db)
        usecase = RegisterUserUseCase(user_repo)
        user = User(
            id=str(uuid.uuid4()),
            name=data.name,
            email=Email(data.email),
            password=data.password, 
        )
        await usecase.execute(user)
        return MessageOutput(
            message="User registered successfully"
        )
    except PasswordValidationError as p:
        raise HTTPException(status_code=400, detail=str(p))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Erro inesperado no registro: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


# ----------------------
# Login
# ----------------------


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Fazer o Login do usuário",
    description="Autentica um usuário com email e senha forte.",
)
async def login_user(
    data: LoginUserInput,
    user_repo: UserRepository = Depends(get_user_repository),
):
    try:
        usecase = LoginUserUseCase(user_repo)
        user = await usecase.execute(Email(data.email), data.password) 

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token(data={"sub": user.id})
        return TokenResponse(
            access_token=token, token_type="bearer", user=UserOutput.from_entity(user)
        )
    except PasswordValidationError as p:
        raise HTTPException(status_code=400, detail=str(p))
    except ValueError as e: 
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        print(f"Erro inesperado no login: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


# ----------------------
# Get Current User
# ----------------------


@router.get(
    "/me",
    response_model=UserOutput,
    summary="Informar os dados do usuário atual",
    description="Retorna os dados do usuário atual.",
)
async def get_me_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer), # <-- Mude aqui para security_bearer
    user: User = Depends(get_current_user),
):
    print(f"DEBUG: current_user ID in get_me_user: {user.id if user else 'None'} Type: {type(user)}") # Adicione print aqui também
    try:
        return UserOutput.from_entity(user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Erro inesperado ao obter usuário atual: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")