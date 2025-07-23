from pydantic import BaseModel, Field
from typing import List, Optional, Annotated

class RecipeInput(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Título da receita")
    ingredients: Annotated[List[str], Field(min_items=1, description="Lista de ingredientes")]
    instructions: Annotated[List[str], Field(min_items=1, description="Lista de instruções")]
    is_public: bool = Field(True, description="Indica se a receita é pública")

class RecipeOutput(BaseModel):
    id: str = Field(..., description="ID da receita")
    title: str = Field(..., description="Título da receita")
    ingredients: List[str] = Field(..., description="Lista de ingredientes")
    instructions: List[str] = Field(..., description="Lista de instruções")
    is_public: bool = Field(..., description="Indica se a receita é pública")

    @classmethod
    def from_entity(cls, recipe):
        return cls(
            id=recipe.id,
            title=recipe.title,
            ingredients=recipe.ingredients,
            instructions=recipe.instructions,
            is_public=recipe.is_public,
        )

class RecipeFavoriteResponse(BaseModel):
    message: str
    recipe_id: str