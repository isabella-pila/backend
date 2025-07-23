# petfit/usecases/recipe/get_user_favorite_recipes.py

from petfit.domain.entities.recipe import Recipe
from petfit.domain.entities.user import User
from petfit.domain.repositories.recipe_repository import RecipeRepository
from typing import List

class GetUserFavoriteRecipesUseCase:
    def __init__(self, repository: RecipeRepository):
        self.repository = repository

    async def execute(self, user: User) -> List[Recipe]:
        """Obtém todas as receitas favoritas de um usuário."""
        return await self.repository.get_user_favorite_recipes(user)