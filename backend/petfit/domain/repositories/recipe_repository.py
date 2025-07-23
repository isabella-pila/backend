# petfit/domain/repositories/recipe_repository.py
#oigit 
from abc import ABC, abstractmethod
from typing import List, Optional
from petfit.domain.entities.recipe import Recipe
from petfit.domain.entities.user import User # Para tipagem nas operações de favoritos

class RecipeRepository(ABC):
    @abstractmethod
    async def create(self, recipe: Recipe) -> Recipe:
        """Cria uma nova receita."""
        pass

    @abstractmethod
    async def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """Obtém uma receita pelo ID."""
        pass

    @abstractmethod
    async def get_all_public_recipes(self) -> Recipe:
        """Obtém todas as receitas públicas."""
        pass

    @abstractmethod
    async def add_favorite(self, user: User, recipe: Recipe) -> bool:
        """Adiciona uma receita aos favoritos de um usuário. Retorna True se adicionado com sucesso."""
        pass

    @abstractmethod
    async def remove_favorite(self, user: User, recipe: Recipe) -> bool:
        """Remove uma receita dos favoritos de um usuário. Retorna True se removido com sucesso."""
        pass

    @abstractmethod
    async def get_user_favorite_recipes(self, user: User) -> List[Recipe]:
        """Obtém todas as receitas favoritas de um usuário."""
        pass

    @abstractmethod
    async def is_favorite(self, user: User, recipe: Recipe) -> bool:
        """Verifica se uma receita é favorita de um usuário."""
        pass

    @abstractmethod
    async def update(self, recipe: Recipe) -> Optional[Recipe]:
        """Atualiza uma receita existente."""
        pass

    @abstractmethod
    async def delete(self, recipe_id: str) -> bool:
        """Deleta uma receita pelo ID. Retorna True se deletado com sucesso."""
        pass