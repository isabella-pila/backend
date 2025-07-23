# petfit/infra/repositories/sqlalchemy/sqlalchemy_recipe_repository.py

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import exc # Para tratamento de exceções de DB
from sqlalchemy.orm import selectinload

from petfit.domain.entities.recipe import Recipe
from petfit.domain.entities.user import User
from petfit.domain.repositories.recipe_repository import RecipeRepository
from petfit.infra.models.recipe_model import RecipeModel
from petfit.infra.models.user_model import UserModel # Necessário para carregar usuários e seus favoritos
# Não precisa importar user_favorite_recipes_table aqui diretamente para relacionamentos.

class SQLAlchemyRecipeRepository(RecipeRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, recipe: Recipe) -> Recipe:
        model = RecipeModel.from_entity(recipe)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        recipe.id = model.id # Atualiza o ID da entidade
        return model.to_entity()

    async def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        stmt = select(RecipeModel).where(RecipeModel.id == recipe_id)
        result = await self._session.execute(stmt)
        recipe_model = result.scalar_one_or_none()
        return recipe_model.to_entity() if recipe_model else None

    async def get_all_public_recipes(self) -> List[Recipe]:
        stmt = select(RecipeModel).where(RecipeModel.is_public == True)
        result = await self._session.execute(stmt)
        return [model.to_entity() for model in result.scalars().all()]

    async def add_favorite(self, user: User, recipe: Recipe) -> bool:
        # Carregar o UserModel completo (com favorite_recipes populadas)
        user_model_stmt = select(UserModel).where(UserModel.id == user.id)
        user_model_result = await self._session.execute(user_model_stmt)
        user_model = user_model_result.scalar_one_or_none()
        if not user_model:
            return False # Usuário não encontrado

        # Carregar o RecipeModel
        recipe_model_stmt = select(RecipeModel).where(RecipeModel.id == recipe.id)
        recipe_model_result = await self._session.execute(recipe_model_stmt)
        recipe_model = recipe_model_result.scalar_one_or_none()
        if not recipe_model:
            return False # Receita não encontrada

        if recipe_model not in user_model.favorite_recipes: # Verifica se já é favorito
            user_model.favorite_recipes.append(recipe_model)
            try:
                await self._session.commit()
                await self._session.refresh(user_model) # Opcional: refresh para garantir o estado
                return True
            except exc.IntegrityError: # Caso haja uma violação de unicidade (já favoritou)
                await self._session.rollback()
                return False
        return False # Já era favorito

    async def remove_favorite(self, user: User, recipe: Recipe) -> bool:
        user_model_stmt = select(UserModel).where(UserModel.id == user.id)
        user_model_result = await self._session.execute(user_model_stmt)
        user_model = user_model_result.scalar_one_or_none()
        if not user_model:
            return False

        recipe_model_stmt = select(RecipeModel).where(RecipeModel.id == recipe.id)
        recipe_model_result = await self._session.execute(recipe_model_stmt)
        recipe_model = recipe_model_result.scalar_one_or_none()
        if not recipe_model:
            return False

        if recipe_model in user_model.favorite_recipes:
            user_model.favorite_recipes.remove(recipe_model)
            await self._session.commit()
            await self._session.refresh(user_model) # Opcional: refresh para garantir o estado
            return True
        return False # Não era favorito para ser removido

    async def get_user_favorite_recipes(self, user: User) -> List[Recipe]:
        # Para carregar os favoritos, precisamos carregar o UserModel com a relação populada
        # Usa `selectinload` para carregar a relação `favorite_recipes` na mesma consulta
        stmt = select(UserModel).options(selectinload(UserModel.favorite_recipes)).where(UserModel.id == user.id)
        result = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()
        if user_model:
            # Converte os RecipeModel para entidades Recipe
            return [recipe_model.to_entity() for recipe_model in user_model.favorite_recipes]
        return []

    async def update(self, recipe: Recipe) -> Optional[Recipe]:
        # Implementação para atualizar uma receita
        existing_recipe = await self._session.get(RecipeModel, recipe.id)
        if not existing_recipe:
            return None
        
        # Atualiza os campos
        existing_recipe.title = recipe.title
        existing_recipe.ingredients = recipe.ingredients
        existing_recipe.instructions = recipe.instructions
        existing_recipe.is_public = recipe.is_public
        
        await self._session.commit()
        await self._session.refresh(existing_recipe)
        return existing_recipe.to_entity()

    async def delete(self, recipe_id: str) -> bool:
        # Implementação para deletar uma receita
        recipe_to_delete = await self._session.get(RecipeModel, recipe_id)
        if not recipe_to_delete:
            return False
        
        await self._session.delete(recipe_to_delete)
        await self._session.commit()
        return True
    
    async def is_favorite(self, user: User, recipe: Recipe) -> bool:
            """Verifica se uma receita é favorita de um usuário."""
            # Carregar o UserModel com suas receitas favoritas
            stmt = select(UserModel).options(selectinload(UserModel.favorite_recipes)).where(UserModel.id == user.id)
            result = await self._session.execute(stmt)
            user_model = result.scalar_one_or_none()

            if user_model:
                # Verificar se a receita está na lista de favoritos do usuário
                # Precisamos do RecipeModel para fazer a comparação direta no relacionamento
                recipe_model_stmt = select(RecipeModel).where(RecipeModel.id == recipe.id)
                recipe_model_result = await self._session.execute(recipe_model_stmt)
                recipe_model = recipe_model_result.scalar_one_or_none()

                if recipe_model and recipe_model in user_model.favorite_recipes:
                    return True
            return False