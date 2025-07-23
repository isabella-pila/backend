from petfit.domain.repositories.recipe_repository import RecipeRepository
from petfit.domain.entities.recipe import Recipe
from typing import List, Optional


class InMemoryRecipeRepository(RecipeRepository):
    def __init__(self):
        self._recipes = {}

    def get_all(self) -> List[Recipe]:
        return list(self._recipes.values())

    def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        return self._recipes.get(recipe_id)

    def create(self, recipe: Recipe) -> Optional[Recipe]:
        self._recipes[recipe.id] = recipe
        return recipe

    def delete(self, post_id: str) -> None:
        self._recipes.pop(post_id, None)