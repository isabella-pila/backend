# petfit/infra/models/user_model.py
from __future__ import annotations
import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped, mapped_column
from petfit.domain.entities.user import User
from petfit.domain.value_objects.email_vo import Email
from petfit.domain.value_objects.password import Password
import uuid
from petfit.infra.database import Base
from petfit.infra.models.recipe_user_model import user_favorite_recipes_table # <--- MUDANÇA AQUI!
from typing import List



class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        sa.String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    email: Mapped[str] = mapped_column(sa.String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(sa.String, nullable=False) 

    favorite_recipes: Mapped[List["RecipeModel"]] = relationship(
        "RecipeModel",
        secondary=user_favorite_recipes_table,
        back_populates="favorite_of_users",
        lazy="selectin"
    )
    
    @classmethod
    def from_entity(cls, entity: User) -> "UserModel":
        return cls(
            id=entity.id,
            name=entity.name,
            email=str(entity.email),
            password=entity.password.hashed_value(),
        )

    def to_entity(self) -> User:
        return User(
            id=self.id,
            name=self.name,
            email=Email(self.email),
            password=Password(self.password, hashed=True),
        )