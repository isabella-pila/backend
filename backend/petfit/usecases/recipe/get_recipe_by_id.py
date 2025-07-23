# petfit/usecases/recipe/get_recipe_by_id.py

from petfit.domain.entities.recipe import Recipe
from petfit.domain.repositories.recipe_repository import RecipeRepository
from typing import Optional

class GetRecipeByIdUseCase:
    def __init__(self, repository: RecipeRepository):
        self.repository = repository

    async def execute(self, recipe_id: str) -> Optional[Recipe]:
        """Obtém uma receita específica pelo ID."""
        return await self.repository.get_by_id(recipe_id)