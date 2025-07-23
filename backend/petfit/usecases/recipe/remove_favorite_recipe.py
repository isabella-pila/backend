# petfit/usecases/recipe/remove_favorite_recipe.py

from petfit.domain.entities.recipe import Recipe
from petfit.domain.entities.user import User
from petfit.domain.repositories.recipe_repository import RecipeRepository

class RemoveFavoriteRecipeUseCase:
    def __init__(self, repository: RecipeRepository):
        self.repository = repository

    async def execute(self, user: User, recipe_id: str) -> bool:
        """Remove uma receita dos favoritos de um usuário.
        Retorna True se removido com sucesso, False caso contrário (ex: não era favorito ou receita não existe).
        """
        # Obtenha a entidade Recipe completa
        recipe = await self.repository.get_by_id(recipe_id)
        if not recipe:
            raise ValueError(f"Recipe with ID {recipe_id} not found.")

        return await self.repository.remove_favorite(user, recipe)