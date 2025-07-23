# tests/usecases/test_recipe_usecases.py

import pytest
from unittest.mock import AsyncMock, MagicMock

# Importe suas entidades e Value Objects
# (Ajuste os imports se a estrutura do seu projeto for diferente)
from petfit.domain.entities.user import User
from petfit.domain.entities.recipe import Recipe
from petfit.domain.value_objects.email_vo import Email
from petfit.domain.value_objects.password import Password

# Importe TODOS os seus casos de uso de receita
from petfit.usecases.recipe.add_favorite_recipe import AddFavoriteRecipeUseCase
from petfit.usecases.recipe.create_recipe import CreateRecipeUseCase
from petfit.usecases.recipe.delete_recipe import DeleteRecipeUseCase
from petfit.usecases.recipe.get_all_recipes import GetAllRecipesUseCase
from petfit.usecases.recipe.get_recipe_by_id import GetRecipeByIdUseCase
from petfit.usecases.recipe.get_user_favorite_recipes import GetUserFavoriteRecipesUseCase
from petfit.usecases.recipe.remove_favorite_recipe import RemoveFavoriteRecipeUseCase
from petfit.usecases.recipe.update_recipe import UpdateRecipeUseCase

# -- Fixtures: Objetos reutilizáveis para os testes --

@pytest.fixture
def mock_recipe_repo():
    """Cria um mock assíncrono para o RecipeRepository."""
    return AsyncMock()

@pytest.fixture
def sample_user():
    """Cria uma instância de User para os testes."""
    return User(
        id="user-123",
        name="Test User",
        email=Email("test@example.com"),
        password=Password("ValidPass@123")
    )

@pytest.fixture
def sample_recipe():
    """Cria uma instância de Recipe para os testes."""
    return Recipe(
        id="recipe-456",
        title="Bolo de Cenoura",
        ingredients="Cenoura, farinha, ovos, óleo",
        instructions="Misture tudo e asse.",
        is_public=True
    )

# -- Testes para cada Caso de Uso --

@pytest.mark.asyncio
async def test_add_favorite_recipe_success(mock_recipe_repo, sample_user, sample_recipe):
    """Testa adicionar uma receita aos favoritos com sucesso."""
    # Arrange: Configura os mocks
    mock_recipe_repo.get_by_id.return_value = sample_recipe
    mock_recipe_repo.add_favorite.return_value = True
    use_case = AddFavoriteRecipeUseCase(mock_recipe_repo)

    # Act: Executa o caso de uso
    result = await use_case.execute(user=sample_user, recipe_id="recipe-456")

    # Assert: Verifica o resultado e as chamadas
    assert result is True
    mock_recipe_repo.get_by_id.assert_called_once_with("recipe-456")
    mock_recipe_repo.add_favorite.assert_called_once_with(sample_user, sample_recipe)

@pytest.mark.asyncio
async def test_add_favorite_recipe_not_found(mock_recipe_repo, sample_user):
    """Testa adicionar uma receita que não existe, esperando um erro."""
    # Arrange
    mock_recipe_repo.get_by_id.return_value = None
    use_case = AddFavoriteRecipeUseCase(mock_recipe_repo)

    # Act & Assert
    with pytest.raises(ValueError, match="Recipe with ID recipe-999 not found."):
        await use_case.execute(user=sample_user, recipe_id="recipe-999")
    mock_recipe_repo.add_favorite.assert_not_called()

@pytest.mark.asyncio
async def test_create_recipe(mock_recipe_repo, sample_recipe):
    """Testa a criação de uma nova receita."""
    # Arrange
    mock_recipe_repo.create.return_value = sample_recipe
    use_case = CreateRecipeUseCase(mock_recipe_repo)

    # Act
    created_recipe = await use_case.execute(recipe=sample_recipe)

    # Assert
    assert created_recipe == sample_recipe
    mock_recipe_repo.create.assert_called_once_with(sample_recipe)

@pytest.mark.asyncio
async def test_delete_recipe(mock_recipe_repo):
    """Testa a deleção de uma receita."""
    # Arrange
    mock_recipe_repo.delete.return_value = True
    use_case = DeleteRecipeUseCase(mock_recipe_repo)

    # Act
    result = await use_case.execute(recipe_id="recipe-456")

    # Assert
    assert result is True
    mock_recipe_repo.delete.assert_called_once_with("recipe-456")

@pytest.mark.asyncio
async def test_get_all_recipes(mock_recipe_repo, sample_recipe):
    """Testa a busca por todas as receitas."""
    # Arrange
    mock_recipe_repo.get_all_public_recipes.return_value = [sample_recipe, sample_recipe]
    use_case = GetAllRecipesUseCase(mock_recipe_repo)

    # Act
    recipes = await use_case.execute()

    # Assert
    assert len(recipes) == 2
    assert recipes[0] == sample_recipe
    mock_recipe_repo.get_all_public_recipes.assert_called_once()

@pytest.mark.asyncio
async def test_get_recipe_by_id(mock_recipe_repo, sample_recipe):
    """Testa a busca de uma receita por ID."""
    # Arrange
    mock_recipe_repo.get_by_id.return_value = sample_recipe
    use_case = GetRecipeByIdUseCase(mock_recipe_repo)

    # Act
    recipe = await use_case.execute(recipe_id="recipe-456")

    # Assert
    assert recipe == sample_recipe
    mock_recipe_repo.get_by_id.assert_called_once_with("recipe-456")

@pytest.mark.asyncio
async def test_get_user_favorite_recipes(mock_recipe_repo, sample_user, sample_recipe):
    """Testa a busca pelas receitas favoritas de um usuário."""
    # Arrange
    mock_recipe_repo.get_user_favorite_recipes.return_value = [sample_recipe]
    use_case = GetUserFavoriteRecipesUseCase(mock_recipe_repo)

    # Act
    favorites = await use_case.execute(user=sample_user)

    # Assert
    assert len(favorites) == 1
    assert favorites[0] == sample_recipe
    mock_recipe_repo.get_user_favorite_recipes.assert_called_once_with(sample_user)

@pytest.mark.asyncio
async def test_remove_favorite_recipe(mock_recipe_repo, sample_user, sample_recipe):
    """Testa a remoção de uma receita dos favoritos."""
    # Arrange
    mock_recipe_repo.get_by_id.return_value = sample_recipe
    mock_recipe_repo.remove_favorite.return_value = True
    use_case = RemoveFavoriteRecipeUseCase(mock_recipe_repo)

    # Act
    result = await use_case.execute(user=sample_user, recipe_id="recipe-456")

    # Assert
    assert result is True
    mock_recipe_repo.get_by_id.assert_called_once_with("recipe-456")
    mock_recipe_repo.remove_favorite.assert_called_once_with(sample_user, sample_recipe)
    
@pytest.mark.asyncio
async def test_update_recipe(mock_recipe_repo, sample_recipe):
    """Testa a atualização de uma receita."""
    # Arrange
    # Simula que a receita atualizada é retornada
    updated_recipe = sample_recipe
    updated_recipe.title = "Novo Título do Bolo"
    mock_recipe_repo.update.return_value = updated_recipe
    use_case = UpdateRecipeUseCase(mock_recipe_repo)
    
    # Act
    result = await use_case.execute(recipe=updated_recipe)
    
    # Assert
    assert result.title == "Novo Título do Bolo"
    mock_recipe_repo.update.assert_called_once_with(updated_recipe)