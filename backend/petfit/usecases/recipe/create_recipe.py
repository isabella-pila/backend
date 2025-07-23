# petfit/usecases/recipe/create_recipe.py

from petfit.domain.entities.recipe import Recipe
from petfit.domain.repositories.recipe_repository import RecipeRepository
from typing import Optional

class CreateRecipeUseCase:
    def __init__(self, repository: RecipeRepository):
        self.repository = repository

    async def execute(self, recipe: Recipe) -> Recipe:
        """Cria uma nova receita."""
        # Aqui você poderia adicionar lógicas de negócio adicionais antes de criar
        # Ex: verificar duplicidade de título, padronizar dados, etc.
        return await self.repository.create(recipe)