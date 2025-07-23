# petfit/usecases/recipe/get_all_recipes.py

from petfit.domain.entities.recipe import Recipe
from petfit.domain.repositories.recipe_repository import RecipeRepository
from typing import List

class GetAllRecipesUseCase:
    def __init__(self, repository: RecipeRepository):
        self.repository = repository

    async def execute(self) -> List[Recipe]:
        """Obtém todas as receitas públicas."""
        return await self.repository.get_all_public_recipes()