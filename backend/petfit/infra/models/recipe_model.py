# petfit/infra/models/recipe_model.py
from __future__ import annotations
import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped, mapped_column
from petfit.infra.database import Base
from petfit.domain.entities.recipe import Recipe
import uuid
from typing import List, Optional
from petfit.infra.models.recipe_user_model import user_favorite_recipes_table # <--- ADICIONE ESTA LINHA
from petfit.infra.models.user_model import UserModel


class RecipeModel(Base):
    __tablename__ = "recipes"

    id: Mapped[str] = mapped_column(
        sa.String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(sa.String, nullable=False)
    ingredients: Mapped[List[str]] = mapped_column(sa.ARRAY(sa.String), nullable=False)
    instructions: Mapped[List[str]] = mapped_column(sa.ARRAY(sa.String), nullable=False)
    is_public: Mapped[bool] = mapped_column(sa.Boolean, default=True)

    favorite_of_users: Mapped[List["UserModel"]] = relationship(
        "UserModel",
        secondary=user_favorite_recipes_table,
        back_populates="favorite_recipes",
        lazy="selectin"
    )

    @classmethod
    def from_entity(cls, entity: Recipe) -> "RecipeModel":
        return cls(
            id=entity.id,
            title=entity.title,
            ingredients=entity.ingredients,
            instructions=entity.instructions,
            is_public=entity.is_public,
        )

    def to_entity(self) -> Recipe:
        return Recipe(
            id=self.id,
            title=self.title,
            ingredients=self.ingredients,
            instructions=self.instructions,
            is_public=self.is_public,
        )