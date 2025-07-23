# petfit/usecases/recipe/add_favorite_recipe.py

from petfit.domain.entities.recipe import Recipe
from petfit.domain.entities.user import User
from petfit.domain.repositories.recipe_repository import RecipeRepository

class AddFavoriteRecipeUseCase:
    def __init__(self, repository: RecipeRepository):
        self.repository = repository

    async def execute(self, user: User, recipe_id: str) -> bool:
        """Adiciona uma receita aos favoritos de um usuário.
        Retorna True se adicionado com sucesso, False caso contrário (ex: já era favorito ou receita não existe).
        """
        # Primeiro, obtenha a entidade Recipe completa
        recipe = await self.repository.get_by_id(recipe_id)
        if not recipe:
            # Você pode levantar uma exceção mais específica aqui se preferir
            raise ValueError(f"Recipe with ID {recipe_id} not found.")
        
        # O repositório lida com a lógica de adicionar o relacionamento
        return await self.repository.add_favorite(user, recipe)