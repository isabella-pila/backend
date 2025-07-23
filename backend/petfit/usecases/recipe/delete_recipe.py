# petfit/usecases/recipe/delete_recipe.py

from petfit.domain.repositories.recipe_repository import RecipeRepository

class DeleteRecipeUseCase:
    def __init__(self, repository: RecipeRepository):
        self.repository = repository

    async def execute(self, recipe_id: str) -> bool:
        """Deleta uma receita pelo ID."""
        return await self.repository.delete(recipe_id)