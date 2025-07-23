# env.py
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv
load_dotenv()

from petfit.infra.database import Base # <--- Ajuste seu caminho aqui!
from petfit.infra.models.user_model import UserModel # <--- Ajuste seu caminho aqui!
from petfit.infra.models.recipe_model import RecipeModel 

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = os.environ.get("DATABASE_URL_ALEMBIC") # <--- Use a URL síncrona aqui!
    if url is None:
        raise Exception("A variável de ambiente 'DATABASE_URL_ALEMBIC' não foi definida.")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    url = os.environ.get("DATABASE_URL_ALEMBIC") # <--- E aqui também!
    if url is None:
        raise Exception("A variável de ambiente 'DATABASE_URL_ALEMBIC' não foi definida.")

    connectable = engine_from_config(
        {"sqlalchemy.url": url}, # Passa a URL síncrona
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()