# tests/usecases/test_user_usecases.py

import pytest
from unittest.mock import AsyncMock, MagicMock

# Importe suas entidades e Value Objects
from petfit.domain.entities.user import User
from petfit.domain.value_objects.email_vo import Email
from petfit.domain.value_objects.password import Password

# Importe TODOS os seus casos de uso de usuário
from petfit.usecases.user.get_current_user import GetCurrentUserUseCase
from petfit.usecases.user.login_user import LoginUserUseCase
from petfit.usecases.user.logout_user import LogoutUserUseCase
from petfit.usecases.user.register_user import RegisterUserUseCase
from petfit.usecases.user.set_current_user import SetCurrentUserUseCase
from petfit.usecases.user.update_user import UpdateUserUseCase

# --- Fixtures: Objetos reutilizáveis para os testes ---

@pytest.fixture
def mock_user_repo():
    """Cria um mock assíncrono para o UserRepository."""
    # Usamos AsyncMock que serve tanto para métodos sync quanto async
    return AsyncMock()

@pytest.fixture
def sample_user(sample_password):
    """Cria uma instância de User para os testes."""
    return User(
        id="user-123",
        name="Test User",
        email=Email("test@example.com"),
        password=sample_password
    )

@pytest.fixture
def sample_password():
    """Cria um mock para o objeto Password, permitindo controlar o método verify."""
    # Usamos MagicMock porque Password não é async
    password_mock = MagicMock(spec=Password)
    password_mock.verify.return_value = True # Sucesso por padrão
    return password_mock

# --- Testes para cada Caso de Uso ---

@pytest.mark.asyncio
async def test_get_current_user_success(mock_user_repo, sample_user):
    """Testa obter o usuário atual com sucesso."""
    # Arrange
    # Simula um "model" que tem o método to_entity()
    mock_model = MagicMock()
    mock_model.to_entity.return_value = sample_user
    mock_user_repo.get_user_by_id.return_value = mock_model
    
    use_case = GetCurrentUserUseCase(mock_user_repo)

    # Act
    result = await use_case.execute(user_id="user-123")

    # Assert
    assert result == sample_user
    mock_user_repo.get_user_by_id.assert_called_once_with("user-123")
    mock_model.to_entity.assert_called_once()

@pytest.mark.asyncio
async def test_get_current_user_not_found(mock_user_repo):
    """Testa o caso em que o usuário não é encontrado."""
    # Arrange
    mock_user_repo.get_user_by_id.return_value = None
    use_case = GetCurrentUserUseCase(mock_user_repo)

    # Act
    result = await use_case.execute(user_id="user-not-found")

    # Assert
    assert result is None

@pytest.mark.asyncio
async def test_login_user_success(mock_user_repo, sample_user):
    """Testa o login com sucesso."""
    # Arrange
    mock_user_repo.login.return_value = sample_user
    use_case = LoginUserUseCase(mock_user_repo)

    # Act
    result = await use_case.execute(email=sample_user.email, plain_password="correct_password")

    # Assert
    assert result == sample_user
    sample_user.password.verify.assert_called_once_with("correct_password")

@pytest.mark.asyncio
async def test_login_user_not_found(mock_user_repo):
    """Testa o login com um email que não existe."""
    # Arrange
    mock_user_repo.login.return_value = None
    use_case = LoginUserUseCase(mock_user_repo)

    # Act
    result = await use_case.execute(email=Email("not@found.com"), plain_password="any_password")
    
    # Assert
    assert result is None

@pytest.mark.asyncio
async def test_login_incorrect_password(mock_user_repo, sample_user):
    """Testa o login com a senha incorreta."""
    # Arrange
    sample_user.password.verify.return_value = False # Simula a falha na verificação
    mock_user_repo.login.return_value = sample_user
    use_case = LoginUserUseCase(mock_user_repo)

    # Act
    result = await use_case.execute(email=sample_user.email, plain_password="wrong_password")

    # Assert
    assert result is None
    sample_user.password.verify.assert_called_once_with("wrong_password")

def test_logout_user(mock_user_repo):
    """Testa o caso de uso de logout, que é síncrono."""
    # Arrange
    use_case = LogoutUserUseCase(mock_user_repo)

    # Act
    use_case.execute()

    # Assert
    mock_user_repo.user_logout.assert_called_once()

@pytest.mark.asyncio
async def test_register_user_success(mock_user_repo, sample_user):
    """Testa o registro de um novo usuário com sucesso."""
    # Arrange
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.register.return_value = sample_user
    use_case = RegisterUserUseCase(mock_user_repo)

    # Act
    result = await use_case.execute(user=sample_user)

    # Assert
    assert result == sample_user
    mock_user_repo.get_by_email.assert_called_once_with(sample_user.email)
    mock_user_repo.register.assert_called_once_with(sample_user)

@pytest.mark.asyncio
async def test_register_user_email_exists(mock_user_repo, sample_user):
    """Testa a falha no registro quando o email já existe."""
    # Arrange
    mock_user_repo.get_by_email.return_value = sample_user
    use_case = RegisterUserUseCase(mock_user_repo)

    # Act & Assert
    with pytest.raises(ValueError, match="User with this email already exists"):
        await use_case.execute(user=sample_user)
    
    mock_user_repo.register.assert_not_called()

def test_set_current_user(mock_user_repo, sample_user):
    """Testa o caso de uso síncrono para definir o usuário atual."""
    # Arrange
    use_case = SetCurrentUserUseCase(mock_user_repo)

    # Act
    use_case.execute(user=sample_user)

    # Assert
    mock_user_repo.set_current_user.assert_called_once_with(sample_user)

@pytest.mark.asyncio
async def test_update_user(mock_user_repo, sample_user):
    """Testa o caso de uso síncrono para atualizar um usuário."""
    # Arrange
    mock_user_repo.update.return_value = sample_user
    use_case = UpdateUserUseCase(mock_user_repo)

    # Act
    result = await use_case.execute(user=sample_user)

    # Assert
    assert result == sample_user
    mock_user_repo.update.assert_called_once_with(sample_user)