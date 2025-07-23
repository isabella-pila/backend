# petfit/infra/models/association_tables.py
from __future__ import annotations
import sqlalchemy as sa
from petfit.infra.database import Base # Certifique-se de importar Base aqui

# Tabela de associação para o relacionamento muitos-para-muitos (usuário favorito receitas)
user_favorite_recipes_table = sa.Table(
    "user_favorite_recipes",
    Base.metadata,
    sa.Column("user_id", sa.String, sa.ForeignKey("users.id"), primary_key=True),
    sa.Column("recipe_id", sa.String, sa.ForeignKey("recipes.id"), primary_key=True)
)