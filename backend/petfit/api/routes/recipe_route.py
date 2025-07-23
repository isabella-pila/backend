# petfit/api/routes/recipe_route.py

from fastapi import APIRouter, HTTPException, Depends, status, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from petfit.domain.entities.user import User
from petfit.domain.entities.recipe import Recipe 
# Importe get_current_user e security_bearer do deps.py
from petfit.api.deps import get_db_session, get_recipe_repository, get_current_user, security_bearer # <-- ADICIONADO security_bearer
from petfit.domain.repositories.recipe_repository import RecipeRepository

from petfit.api.schemas.recipe_schema import (
    RecipeInput,
    RecipeOutput,
    RecipeFavoriteResponse
)
from petfit.api.schemas.message_schema import MessageOutput 
from fastapi.security import HTTPAuthorizationCredentials # <-- ADICIONADO para tipagem

# Use cases
from petfit.usecases.recipe.create_recipe import CreateRecipeUseCase
from petfit.usecases.recipe.get_all_recipes import GetAllRecipesUseCase
from petfit.usecases.recipe.get_recipe_by_id import GetRecipeByIdUseCase
from petfit.usecases.recipe.add_favorite_recipe import AddFavoriteRecipeUseCase
from petfit.usecases.recipe.remove_favorite_recipe import RemoveFavoriteRecipeUseCase
from petfit.usecases.recipe.get_user_favorite_recipes import GetUserFavoriteRecipesUseCase
from petfit.usecases.recipe.update_recipe import UpdateRecipeUseCase
from petfit.usecases.recipe.delete_recipe import DeleteRecipeUseCase

import uuid 

router = APIRouter()

# ----------------------
# Create Recipe (Pode ser público ou privado inicialmente)
# ----------------------
@router.post(
    "/recipes",
    response_model=RecipeOutput,
    summary="Criar nova receita",
    description="Cria uma nova receita.",
    status_code=status.HTTP_201_CREATED,
    tags=["Recipes"]
)
async def create_recipe(
    recipe_input: RecipeInput, 
    db: AsyncSession = Depends(get_db_session),
):
    try:
        recipe_repo = await get_recipe_repository(db)
        usecase = CreateRecipeUseCase(recipe_repo)
        
        recipe_entity = Recipe(
            id=str(uuid.uuid4()),
            title=recipe_input.title,
            ingredients=", ".join(recipe_input.ingredients),         
            instructions="\n".join(recipe_input.instructions),       
            is_public=recipe_input.is_public
            )
        
        created_recipe = await usecase.execute(recipe_entity)
        return RecipeOutput.from_entity(created_recipe)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Erro inesperado ao criar receita: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

# ----------------------
# Get All Public Recipes
# ----------------------
@router.get(
    "/recipes",
    response_model=List[RecipeOutput],
    summary="Listar todas as receitas públicas",
    description="Retorna uma lista de todas as receitas marcadas como públicas.",
    tags=["Recipes"]
)
async def get_all_public_recipes(
    db: AsyncSession = Depends(get_db_session),
):
    try:
        recipe_repo = await get_recipe_repository(db)
        usecase = GetAllRecipesUseCase(recipe_repo)
        recipes = await usecase.execute()
        return [RecipeOutput.from_entity(r) for r in recipes]
    except Exception as e:
        print(f"Erro inesperado ao listar receitas públicas: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

# ----------------------
# Get Recipe by ID
# ----------------------
@router.get(
    "/recipes/{recipe_id}",
    response_model=RecipeOutput,
    summary="Obter receita por ID",
    description="Retorna os detalhes de uma receita específica pelo seu ID.",
    tags=["Recipes"]
)
async def get_recipe_by_id(
    recipe_id: str = Path(..., description="ID da receita a ser obtida"),
    db: AsyncSession = Depends(get_db_session),
):
    try:
        recipe_repo = await get_recipe_repository(db)
        usecase = GetRecipeByIdUseCase(recipe_repo)
        recipe = await usecase.execute(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found.")
        return RecipeOutput.from_entity(recipe)
    except Exception as e:
        print(f"Erro inesperado ao obter receita por ID: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


# ----------------------
# Add Recipe to Favorites (AUTHENTICATED)
# ----------------------
@router.post(
    "/recipes/{recipe_id}/favorite",
    response_model=MessageOutput, 
    summary="Adicionar receita aos favoritos",
    description="Adiciona uma receita específica aos favoritos do usuário logado.",
    status_code=status.HTTP_200_OK, 
    tags=["Recipes", "Favorites"],
    # Removido: dependencies=[Depends(get_current_user)] 
)
async def add_recipe_to_favorites(
    recipe_id: str = Path(..., description="ID da receita a ser favoritada"),
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer), # <-- Adicionado aqui para consistência
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db_session),
):
    print(f"DEBUG: current_user ID in add_recipe_to_favorites: {current_user.id if current_user else 'None'} Type: {type(current_user)}")
    try:
        recipe_repo = await get_recipe_repository(db)
        usecase = AddFavoriteRecipeUseCase(recipe_repo)
        
        added = await usecase.execute(current_user, recipe_id)
        if added:
            return MessageOutput(message="Recipe added to favorites successfully.")
        else:
            raise HTTPException(status_code=400, detail="Recipe is already in favorites or not found.")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) 
    except HTTPException as e: 
        raise e 
    except Exception as e:
        print(f"Erro inesperado ao adicionar receita aos favoritos: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


# ----------------------
# Remove Recipe from Favorites (AUTHENTICATED)
# ----------------------
@router.delete(
    "/recipes/{recipe_id}/favorite",
    response_model=MessageOutput,
    summary="Remover receita dos favoritos",
    description="Remove uma receita específica dos favoritos do usuário logado.",
    status_code=status.HTTP_200_OK,
    tags=["Recipes", "Favorites"],
    # Removido: dependencies=[Depends(get_current_user)] 
)
async def remove_recipe_from_favorites(
    recipe_id: str = Path(..., description="ID da receita a ser removida dos favoritos"),
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer), # <-- Adicionado aqui
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db_session),
):
    print(f"DEBUG: current_user ID in remove_recipe_from_favorites: {current_user.id if current_user else 'None'} Type: {type(current_user)}")
    try:
        recipe_repo = await get_recipe_repository(db)
        usecase = RemoveFavoriteRecipeUseCase(recipe_repo)
        
        removed = await usecase.execute(current_user, recipe_id)
        if removed:
            return MessageOutput(message="Recipe removed from favorites successfully.")
        else:
            raise HTTPException(status_code=400, detail="Recipe is not in favorites or not found.")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) 
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erro inesperado ao remover receita dos favoritos: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


# ----------------------
# Get User Favorite Recipes (AUTHENTICATED)
# ----------------------
@router.get(
    "/users/me/favorites/recipes", 
    response_model=List[RecipeOutput],
    summary="Listar receitas favoritas do usuário logado",
    description="Retorna uma lista das receitas favoritas do usuário atualmente logado.",
    tags=["Users", "Favorites"],
    # Removido: dependencies=[Depends(get_current_user)] 
)
async def get_my_favorite_recipes(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer), # <-- Adicionado aqui
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    print(f"DEBUG: current_user ID in get_my_favorite_recipes: {current_user.id if current_user else 'None'} Type: {type(current_user)}")
    try:
        recipe_repo = await get_recipe_repository(db)
        usecase = GetUserFavoriteRecipesUseCase(recipe_repo)
        favorite_recipes = await usecase.execute(current_user)
        return [RecipeOutput.from_entity(r) for r in favorite_recipes]
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erro inesperado ao listar favoritos do usuário: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

# ----------------------
# Update Recipe (por ID - precisa de lógica de autorização)
# ----------------------
@router.put(
    "/recipes/{recipe_id}",
    response_model=RecipeOutput,
    summary="Atualizar receita",
    description="Atualiza uma receita existente pelo seu ID. Requer autenticação.",
    tags=["Recipes"],
    # Removido: dependencies=[Depends(get_current_user)] 
)
async def update_recipe_endpoint(
    recipe_id: str = Path(..., description="ID da receita a ser atualizada"),
    recipe_input: RecipeInput = Body(..., description="Dados da receita para atualização"),
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer), # <-- Adicionado aqui
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db_session),
):
    print(f"DEBUG: current_user ID in update_recipe_endpoint: {current_user.id if current_user else 'None'} Type: {type(current_user)}")
    try:
        recipe_repo = await get_recipe_repository(db)
        usecase = UpdateRecipeUseCase(recipe_repo)
        
        updated_recipe_entity = Recipe(
                id=recipe_id,
                title=recipe_input.title,
                ingredients=", ".join(recipe_input.ingredients),         
                instructions="\n".join(recipe_input.instructions),       
                is_public=recipe_input.is_public
            )

        
        updated_recipe = await usecase.execute(updated_recipe_entity)
        if not updated_recipe:
            raise HTTPException(status_code=404, detail="Recipe not found.")
        
        return RecipeOutput.from_entity(updated_recipe)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erro inesperado ao atualizar receita: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

# ----------------------
# Delete Recipe (por ID - precisa de lógica de autorização)
# ----------------------
@router.delete(
    "/recipes/{recipe_id}",
    response_model=MessageOutput,
    summary="Deletar receita",
    description="Deleta uma receita existente pelo seu ID. Requer autenticação.",
    tags=["Recipes"],
    # Removido: dependencies=[Depends(get_current_user)] 
)
async def delete_recipe_endpoint(
    recipe_id: str = Path(..., description="ID da receita a ser deletada"),
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer), # <-- Adicionado aqui
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db_session),
):
    print(f"DEBUG: current_user ID in delete_recipe_endpoint: {current_user.id if current_user else 'None'} Type: {type(current_user)}")
    try:
        recipe_repo = await get_recipe_repository(db)
        usecase = DeleteRecipeUseCase(recipe_repo)
        
        deleted = await usecase.execute(recipe_id)
        if deleted:
            return MessageOutput(message="Recipe deleted successfully.")
        else:
            raise HTTPException(status_code=404, detail="Recipe not found.")
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erro inesperado ao deletar receita: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")