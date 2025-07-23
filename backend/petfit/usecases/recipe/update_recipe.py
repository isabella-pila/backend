# petfit/usecases/recipe/update_recipe.py

from petfit.domain.entities.recipe import Recipe
from petfit.domain.repositories.recipe_repository import RecipeRepository
from typing import Optional

class UpdateRecipeUseCase:
    def __init__(self, repository: RecipeRepository):
        self.repository = repository

    async def execute(self, recipe: Recipe) -> Optional[Recipe]:
        """Atualiza uma receita existente."""
        # Você pode adicionar lógica de negócio aqui, como verificar se o usuário
        # que está tentando atualizar é o proprietário original da receita (se houver)
        return await self.repository.update(recipe)